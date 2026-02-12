#!/usr/bin/env python3
"""med_info.py

API-only medication info retriever.

Sources:
- RxNorm (RxNav): name normalization to RxCUI
- openFDA: drug label + NDC directory
- MedlinePlus Connect: patient-friendly links/summaries by RxCUI

Usage:
  python3 scripts/med_info.py "ibuprofen" [--json]
  python3 scripts/med_info.py "00093-1045-56" [--json]

Env:
  OPENFDA_API_KEY (optional)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


USER_AGENT = "clawdbot-med-info/0.2 (+https://clawhub.ai/DuncanDobbins/med-info)"
TIMEOUT_S = 20

# Best-effort request traceability. Stores *redacted* URLs (api_key removed).
URL_LOG: List[str] = []


def _redact_url(url: str) -> str:
    try:
        p = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
        qs2 = [(k, v) for (k, v) in qs if k.lower() != "api_key"]
        return urllib.parse.urlunparse((p.scheme, p.netloc, p.path, p.params, urllib.parse.urlencode(qs2), p.fragment))
    except Exception:
        return url


def _log_url(url: str) -> None:
    URL_LOG.append(_redact_url(url))


def http_get_json(url: str, headers: Optional[Dict[str, str]] = None, *, allow_404: bool = False) -> Any:
    _log_url(url)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            data = resp.read()
        return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as e:
        if allow_404 and e.code == 404:
            # openFDA returns 404 when there are no matches.
            return {"results": []}
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        raise RuntimeError(f"HTTP {e.code} for {url}: {body[:500]}") from e


def is_probable_ndc(s: str) -> bool:
    s = s.strip()
    # Common patterns: 4-4, 5-3-2, 5-4-1, etc. Also allow digits-only 10/11.
    if re.fullmatch(r"\d{10,11}", s):
        return True
    if re.fullmatch(r"\d{4,5}-\d{3,4}(-\d{1,2})?", s):
        return True
    return False


def is_uuid_like(s: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", s.strip()))


def rxnorm_approximate(term: str, max_entries: int = 5) -> List[Dict[str, Any]]:
    # Docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getApproximateMatch.html
    qs = urllib.parse.urlencode({"term": term, "maxEntries": str(max_entries), "option": "1"})
    url = f"https://rxnav.nlm.nih.gov/REST/approximateTerm.json?{qs}"
    j = http_get_json(url)
    cand = j.get("approximateGroup", {}).get("candidate", [])
    if isinstance(cand, dict):
        cand = [cand]
    return cand


def rxnorm_name_for_rxcui(rxcui: str) -> Optional[str]:
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{urllib.parse.quote(rxcui)}/properties.json"
    j = http_get_json(url)
    props = j.get("properties") or {}
    return props.get("name")


def openfda_url(path: str, query: str, limit: int = 1) -> str:
    base = f"https://api.fda.gov{path}.json"
    params = {"search": query, "limit": str(limit)}
    api_key = os.environ.get("OPENFDA_API_KEY")
    if api_key:
        params["api_key"] = api_key
    return base + "?" + urllib.parse.urlencode(params)


def openfda_label_by_rxcui(rxcui: str) -> Optional[Dict[str, Any]]:
    q = f'openfda.rxcui:"{rxcui}"'
    url = openfda_url("/drug/label", q, limit=1)
    j = http_get_json(url, allow_404=True)
    res = j.get("results")
    if not res:
        return None
    return res[0]


def _as_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def openfda_label_candidates(name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Return candidate openFDA labels for a query, sorted best-first.

    Used for disambiguation and robust fallback when RxCUI search fails.
    """
    nm = _norm(name)
    q = (
        f'(openfda.generic_name:"{name}" '
        f'OR openfda.substance_name:"{name}" '
        f'OR openfda.brand_name:"{name}")'
    )
    url = openfda_url("/drug/label", q, limit=limit)
    j = http_get_json(url, allow_404=True)
    res = j.get("results") or []
    if not res:
        return []

    def score_label(label: Dict[str, Any]) -> Tuple[int, str]:
        of = label.get("openfda") or {}
        subs = [_norm(str(x)) for x in _as_list(of.get("substance_name")) if str(x).strip()]
        gens = [_norm(str(x)) for x in _as_list(of.get("generic_name")) if str(x).strip()]
        brands = [_norm(str(x)) for x in _as_list(of.get("brand_name")) if str(x).strip()]

        s = 0

        # Prefer single-ingredient labels when the query looks like a single ingredient.
        looks_combo = any(tok in nm for tok in [" and ", "/", "+"])
        if not looks_combo:
            if len(subs) == 1:
                s += 50
            elif len(subs) > 1:
                s -= 30

        if nm in subs:
            s += 60
        if nm in gens:
            s += 40
        if nm in brands:
            s += 10

        # Prefer newer effective_time when scores tie.
        et = str(label.get("effective_time") or "")
        return (s, et)

    return sorted(res, key=score_label, reverse=True)


def openfda_label_by_generic_name(name: str) -> Optional[Dict[str, Any]]:
    # Backwards-compatible helper: pick the best candidate.
    cands = openfda_label_candidates(name, limit=10)
    return cands[0] if cands else None


def openfda_label_by_set_id(set_id: str) -> Optional[Dict[str, Any]]:
    # openFDA drug/label supports set_id queries.
    q = f'set_id:"{set_id}"'
    url = openfda_url("/drug/label", q, limit=1)
    j = http_get_json(url, allow_404=True)
    res = j.get("results")
    if not res:
        return None
    return res[0]


def openfda_ndc_lookup(ndc: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Lookup an NDC in openFDA drug/ndc.

    Notes:
    - `product_ndc` is a top-level field.
    - `package_ndc` lives under `packaging[].package_ndc`.
    """
    ndc = (ndc or "").strip()
    parts = [p for p in ndc.split("-") if p]

    product_ndc = None
    package_ndc = None

    if len(parts) == 3:
        package_ndc = ndc
        product_ndc = f"{parts[0]}-{parts[1]}"
    elif len(parts) == 2:
        product_ndc = ndc

    terms: List[str] = []
    if product_ndc:
        terms.append(f'product_ndc:"{product_ndc}"')
    if package_ndc:
        terms.append(f'packaging.package_ndc:"{package_ndc}"')

    if not terms:
        # Fallback: best-effort exact match against both fields.
        terms = [f'product_ndc:"{ndc}"', f'packaging.package_ndc:"{ndc}"']

    q = "(" + " OR ".join(terms) + ")"
    url = openfda_url("/drug/ndc", q, limit=limit)
    j = http_get_json(url, allow_404=True)
    res = j.get("results")
    return res or []


def openfda_enforcement_search(search: str, limit: int = 5) -> List[Dict[str, Any]]:
    url = openfda_url("/drug/enforcement", search, limit=limit)
    j = http_get_json(url, allow_404=True)
    return j.get("results") or []


def openfda_shortages_search(search: str, limit: int = 5) -> List[Dict[str, Any]]:
    # Note: endpoint path is /drug/shortages (not /drug/drugshortages)
    url = openfda_url("/drug/shortages", search, limit=limit)
    j = http_get_json(url, allow_404=True)
    return j.get("results") or []


def medlineplus_by_rxcui(rxcui: str) -> Dict[str, Any]:
    # RxNorm OID: 2.16.840.1.113883.6.88
    params = {
        "knowledgeResponseType": "application/json",
        "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.88",
        "mainSearchCriteria.v.c": rxcui,
        "informationRecipient.languageCode.c": "en",
    }
    url = "https://connect.medlineplus.gov/service?" + urllib.parse.urlencode(params)
    return http_get_json(url)


def pick_best_candidate(candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None

    # Highest score, then lowest rank.
    def key(c: Dict[str, Any]) -> Tuple[float, int]:
        try:
            score = float(c.get("score") or 0)
        except Exception:
            score = 0.0
        try:
            rank = int(c.get("rank") or 999999)
        except Exception:
            rank = 999999
        # Lower rank is better, so invert it.
        return (score, -rank)

    return sorted(candidates, key=key, reverse=True)[0]


def label_section(label: Dict[str, Any], key: str) -> Optional[str]:
    v = label.get(key)
    if not v:
        return None
    if isinstance(v, list):
        # join paragraphs, preserve spacing.
        return "\n\n".join([str(x).strip() for x in v if str(x).strip()])
    return str(v).strip()


def daily_med_url_from_setid(setid: Optional[str]) -> Optional[str]:
    if not setid:
        return None
    return f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={urllib.parse.quote(setid)}"


def _first_of(v: Any) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, list):
        return str(v[0]) if v else None
    return str(v)


def label_candidate_summary(label: Dict[str, Any]) -> Dict[str, Any]:
    of = (label or {}).get("openfda") or {}
    setid = _first_of(of.get("spl_set_id"))
    return {
        "effective_time": label.get("effective_time"),
        "id": label.get("id"),
        "setid": setid,
        "dailymed": daily_med_url_from_setid(setid),
        "brand_name": _first_of(of.get("brand_name")),
        "generic_name": _first_of(of.get("generic_name")),
        "manufacturer_name": _first_of(of.get("manufacturer_name")),
        "route": _first_of(of.get("route")),
        "dosage_form": _first_of(of.get("dosage_form")),
        "substance_name": of.get("substance_name"),
        "product_ndc": _first_of(of.get("product_ndc")),
    }


def collect_text_fields(label: Dict[str, Any]) -> Dict[str, str]:
    """Flatten top-level textual fields from an openFDA label result.

    We only consider top-level keys where values are strings or lists of strings.
    """
    out: Dict[str, str] = {}
    for k, v in (label or {}).items():
        if k == "openfda":
            continue
        if isinstance(v, str):
            s = v.strip()
            if s:
                out[k] = s
        elif isinstance(v, list):
            parts = [str(x).strip() for x in v if str(x).strip()]
            if parts:
                out[k] = "\n\n".join(parts)
    return out


def find_hits(text_fields: Dict[str, str], keywords: List[str], max_total: int = 20) -> List[Dict[str, Any]]:
    """Return compact snippet hits across all fields."""
    hits: List[Dict[str, Any]] = []
    if not keywords:
        return hits

    kws = [k for k in (kw.strip() for kw in keywords) if k]
    if not kws:
        return hits

    for kw in kws:
        pat = re.compile(re.escape(kw), re.IGNORECASE)
        for field, text in text_fields.items():
            for m in pat.finditer(text):
                start = max(0, m.start() - 60)
                end = min(len(text), m.end() + 60)
                snippet = text[start:end].replace("\n", " ").strip()
                hits.append({
                    "keyword": kw,
                    "field": field,
                    "snippet": snippet,
                    "index": m.start(),
                })
                if len(hits) >= max_total:
                    return hits
    return hits


def _compact(s: Optional[str], max_len: int = 280) -> Optional[str]:
    if not s:
        return None
    x = re.sub(r"\s+", " ", str(s)).strip()
    if len(x) <= max_len:
        return x
    return x[: max_len - 1] + "…"


def _parse_sections(sections: List[str]) -> Optional[List[str]]:
    """Parse --sections.

    Accepts comma-separated values, repeatable.
    Returns None when no selection (meaning use defaults).
    """
    if not sections:
        return None
    out: List[str] = []
    for s in sections:
        for part in (p.strip() for p in str(s).split(",")):
            if part:
                out.append(part)
    if not out:
        return None
    if any(x.lower() == "all" for x in out):
        return [
            "boxed_warning",
            "indications_and_usage",
            "dosage_and_administration",
            "contraindications",
            "warnings_and_precautions",
            "drug_interactions",
            "adverse_reactions",
        ]
    return out


def _compact_recall(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "recall_number": r.get("recall_number"),
        "status": r.get("status"),
        "classification": r.get("classification"),
        "recalling_firm": r.get("recalling_firm"),
        "product_description": r.get("product_description"),
        "reason_for_recall": r.get("reason_for_recall"),
        "recall_initiation_date": r.get("recall_initiation_date"),
        "report_date": r.get("report_date"),
        "termination_date": r.get("termination_date"),
    }


def _compact_shortage(r: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": r.get("status"),
        "generic_name": r.get("generic_name"),
        "brand_name": r.get("brand_name"),
        "presentation": r.get("presentation"),
        "package_ndc": r.get("package_ndc"),
        "shortage_reason": r.get("shortage_reason"),
        "availability": r.get("availability"),
        "company_name": r.get("company_name"),
        "update_date": r.get("update_date"),
        "initial_posting_date": r.get("initial_posting_date"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="Drug name, NDC, or set_id")

    # Output / shaping
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    ap.add_argument("--brief", action="store_true", help="Compact human-readable output")
    ap.add_argument(
        "--sections",
        action="append",
        default=[],
        metavar="S",
        help="Comma-separated label sections to print/return (repeatable). Use 'all' for standard full set.",
    )
    ap.add_argument("--print-url", action="store_true", help="Print redacted URLs queried")

    # Disambiguation
    ap.add_argument("--set-id", dest="set_id", help="Force a specific SPL set_id (UUID)")
    ap.add_argument("--candidates", action="store_true", help="Show label candidates for the query")
    ap.add_argument("--pick", type=int, help="Pick Nth candidate label (1-indexed)")

    # Extras
    ap.add_argument("--recalls", action="store_true", help="Include recent recall enforcement matches")
    ap.add_argument("--recalls-max", type=int, default=5, help="Max recall matches (default: 5)")
    ap.add_argument("--shortages", action="store_true", help="Include drug shortage matches")
    ap.add_argument("--shortages-max", type=int, default=5, help="Max shortage matches (default: 5)")

    # Keyword search
    ap.add_argument(
        "--find",
        action="append",
        default=[],
        metavar="KEYWORD",
        help="Find keyword in retrieved label text (repeatable, case-insensitive)",
    )
    ap.add_argument(
        "--find-max",
        type=int,
        default=20,
        help="Max total find hits to return (default: 20)",
    )

    args = ap.parse_args()

    q = args.query.strip()

    out: Dict[str, Any] = {
        "input": {"query": q, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
        "rxnorm": {},
        "openfda": {},
        "medlineplus": {},
        "notes": [],
    }

    rxcui: Optional[str] = None
    rx_name: Optional[str] = None
    selected_sections: Optional[List[str]] = None

    try:
        selected_sections = _parse_sections(args.sections)
        out["input"]["sections"] = selected_sections

        ndc_set_id: Optional[str] = None

        forced_set_id = args.set_id or (q if is_uuid_like(q) else None)
        if forced_set_id:
            out["input"]["type"] = "set_id"
            ndc_set_id = forced_set_id
        elif is_probable_ndc(q):
            out["input"]["type"] = "ndc"
            ndc_results = openfda_ndc_lookup(q)
            out["openfda"]["ndc_results"] = ndc_results

            # If NDC response includes SPL set id and/or RxCUI, use it.
            for r in ndc_results:
                of = r.get("openfda") or {}

                spl_set = of.get("spl_set_id") or []
                if isinstance(spl_set, list) and spl_set:
                    ndc_set_id = str(spl_set[0])

                rxcuis = of.get("rxcui") or []
                if isinstance(rxcuis, list) and rxcuis and not rxcui:
                    rxcui = str(rxcuis[0])

                if ndc_set_id and rxcui:
                    break
        else:
            out["input"]["type"] = "name"

        # Resolve name to RxCUI (only when the input is a drug name).
        if out["input"].get("type") == "name" and not rxcui:
            cand = rxnorm_approximate(q, max_entries=5)
            out["rxnorm"]["candidates"] = cand
            best = pick_best_candidate(cand)
            if best:
                rxcui = str(best.get("rxcui")) if best.get("rxcui") else None
                out["rxnorm"]["best"] = best

        if rxcui or ndc_set_id:
            if rxcui:
                rx_name = rxnorm_name_for_rxcui(rxcui)
                out["rxnorm"]["rxcui"] = rxcui
                out["rxnorm"]["name"] = rx_name

            label_candidates: List[Dict[str, Any]] = []
            if out["input"].get("type") == "name" and (args.candidates or args.pick):
                term = rx_name or q
                label_candidates = openfda_label_candidates(term, limit=10)
                out["openfda"]["candidates"] = [label_candidate_summary(x) for x in label_candidates]

            label = None
            if ndc_set_id:
                out["openfda"]["ndc_set_id"] = ndc_set_id
                label = openfda_label_by_set_id(ndc_set_id)
                if not label:
                    out["notes"].append("No openFDA label found by set_id from NDC/set_id lookup.")

            if not label and args.pick and out["input"].get("type") == "name":
                if not label_candidates:
                    out["notes"].append("No label candidates available to pick from.")
                else:
                    idx = int(args.pick) - 1
                    if 0 <= idx < len(label_candidates):
                        label = label_candidates[idx]
                        out["openfda"]["picked"] = int(args.pick)
                    else:
                        out["notes"].append(f"--pick {args.pick} out of range (1..{len(label_candidates)}).")

            if not label and rxcui:
                label = openfda_label_by_rxcui(rxcui)

            if not label and rx_name:
                out["notes"].append("No openFDA label found by RxCUI, falling back to generic/substance/brand candidates.")
                if label_candidates:
                    label = label_candidates[0]
                else:
                    label = openfda_label_by_generic_name(rx_name)

            if label:
                setid = None
                openfda_block = label.get("openfda") or {}
                # openFDA label sometimes has spl_set_id in openfda
                spl_set_id = openfda_block.get("spl_set_id")
                if isinstance(spl_set_id, list) and spl_set_id:
                    setid = spl_set_id[0]

                section_keys = selected_sections or [
                    "boxed_warning",
                    "indications_and_usage",
                    "dosage_and_administration",
                    "contraindications",
                    "warnings_and_precautions",
                    "drug_interactions",
                    "adverse_reactions",
                ]
                sections = {k: label_section(label, k) for k in section_keys}

                label_obj: Dict[str, Any] = {
                    "effective_time": label.get("effective_time"),
                    "id": label.get("id"),
                    "setid": setid,
                    "dailymed": daily_med_url_from_setid(setid),
                    "openfda": {
                        "brand_name": openfda_block.get("brand_name"),
                        "generic_name": openfda_block.get("generic_name"),
                        "manufacturer_name": openfda_block.get("manufacturer_name"),
                        "product_ndc": openfda_block.get("product_ndc"),
                        "package_ndc": openfda_block.get("package_ndc"),
                        "route": openfda_block.get("route"),
                        "dosage_form": openfda_block.get("dosage_form"),
                        "substance_name": openfda_block.get("substance_name"),
                        "rxcui": openfda_block.get("rxcui"),
                    },
                    "sections": sections,
                }

                if args.find:
                    fields = collect_text_fields(label)
                    label_obj["find"] = {
                        "keywords": args.find,
                        "hits": find_hits(fields, args.find, max_total=max(1, int(args.find_max))),
                    }

                out["openfda"]["label"] = label_obj

                # Optional: recalls
                if args.recalls:
                    product_ndc0 = _first_of(openfda_block.get("product_ndc"))
                    brand0 = _first_of(openfda_block.get("brand_name"))
                    generic0 = _first_of(openfda_block.get("generic_name")) or rx_name or q

                    recall_queries: List[str] = []
                    if product_ndc0:
                        recall_queries.append(f'openfda.product_ndc:"{product_ndc0}"')
                    if brand0:
                        recall_queries.append(f'product_description:"{brand0}"')
                    if generic0:
                        recall_queries.append(f'product_description:"{generic0}"')

                    recalls: List[Dict[str, Any]] = []
                    used_query = None
                    for rq in recall_queries:
                        rr = openfda_enforcement_search(rq, limit=max(1, int(args.recalls_max)))
                        if rr:
                            used_query = rq
                            recalls = rr
                            break
                    out["openfda"]["recalls"] = {
                        "query": used_query,
                        "results": [_compact_recall(r) for r in recalls],
                    }

                # Optional: shortages
                if args.shortages:
                    brand0 = _first_of(openfda_block.get("brand_name"))
                    generic0 = _first_of(openfda_block.get("generic_name")) or q

                    shortage_queries: List[str] = []
                    if generic0:
                        shortage_queries.append(f'generic_name:"{generic0}"')
                    if brand0:
                        shortage_queries.append(f'brand_name:"{brand0}"')
                    if q and q != generic0:
                        shortage_queries.append(f'generic_name:"{q}"')
                        shortage_queries.append(f'brand_name:"{q}"')

                    shortages: List[Dict[str, Any]] = []
                    used_query = None
                    for sq in shortage_queries:
                        sr = openfda_shortages_search(sq, limit=max(1, int(args.shortages_max)))
                        if sr:
                            used_query = sq
                            shortages = sr
                            break
                    out["openfda"]["shortages"] = {
                        "query": used_query,
                        "results": [_compact_shortage(r) for r in shortages],
                    }

            else:
                out["notes"].append("No openFDA label match found.")

            if rxcui:
                try:
                    mpl = medlineplus_by_rxcui(rxcui)
                    out["medlineplus"]["raw"] = mpl

                    # Extract a compact list of results.
                    feed = (mpl or {}).get("feed") or {}
                    entries = feed.get("entry") or []
                    if isinstance(entries, dict):
                        entries = [entries]
                    compact = []
                    for e in entries[:10]:
                        title = e.get("title")
                        if isinstance(title, dict):
                            title = title.get("_value") or title.get("value")
                        link = None
                        links = e.get("link") or []
                        if isinstance(links, dict):
                            links = [links]
                        for l in links:
                            href = l.get("href")
                            if href:
                                link = href
                                break
                        if title or link:
                            compact.append({"title": title, "url": link})
                    out["medlineplus"]["results"] = compact
                except Exception as e:
                    out["notes"].append(f"MedlinePlus Connect lookup failed: {e}")
        else:
            if out["input"].get("type") == "ndc":
                out["notes"].append("No openFDA NDC match found for that code.")
            else:
                out["notes"].append("Could not resolve RxCUI from input.")

    except Exception as e:
        out["error"] = str(e)

    if args.print_url or args.json:
        out.setdefault("debug", {})["urls"] = URL_LOG

    if args.json:
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
        return 0 if "error" not in out else 2

    # Human-readable.
    print(f"Query: {q}")
    if rxcui:
        print(f"RxCUI: {rxcui}" + (f" ({rx_name})" if rx_name else ""))
    else:
        print("RxCUI: (not resolved)")

    label_obj = out.get("openfda", {}).get("label")
    if label_obj:
        print("\nopenFDA label")
        et = label_obj.get("effective_time")
        if et:
            print(f"- effective_time: {et}")
        if label_obj.get("dailymed"):
            print(f"- DailyMed: {label_obj['dailymed']}")

        of = label_obj.get("openfda") or {}
        # Print a compact identifier line when available.
        brand = (of.get("brand_name") or [None])[0] if isinstance(of.get("brand_name"), list) else of.get("brand_name")
        generic = (of.get("generic_name") or [None])[0] if isinstance(of.get("generic_name"), list) else of.get("generic_name")
        mfr = (of.get("manufacturer_name") or [None])[0] if isinstance(of.get("manufacturer_name"), list) else of.get("manufacturer_name")
        if brand or generic or mfr:
            print(f"- product: {brand or ''} {('/ ' + generic) if generic else ''} {('(' + mfr + ')') if mfr else ''}".strip())

        sections = label_obj.get("sections") or {}
        order = [
            ("boxed_warning", "Boxed warning"),
            ("indications_and_usage", "Indications and usage"),
            ("dosage_and_administration", "Dosage and administration"),
            ("contraindications", "Contraindications"),
            ("warnings_and_precautions", "Warnings and precautions"),
            ("drug_interactions", "Drug interactions"),
            ("adverse_reactions", "Adverse reactions"),
        ]
        for k, title in order:
            txt = sections.get(k)
            if not txt:
                continue
            if args.brief:
                txt = _compact(txt, max_len=420) or txt
            print(f"\n{title}\n{txt}")

    # Disambiguation: candidates
    cands = out.get("openfda", {}).get("candidates")
    if args.candidates and cands:
        print("\nCandidates")
        for i, c in enumerate(cands[:10], start=1):
            prod = " / ".join([x for x in [c.get("brand_name"), c.get("generic_name")] if x])
            meta = " ".join([x for x in [c.get("dosage_form"), c.get("route")] if x])
            et = c.get("effective_time") or ""
            setid = c.get("setid") or ""
            dm = c.get("dailymed") or ""
            line = f"{i}. {prod}".strip()
            if meta:
                line += f" | {meta}"
            if et:
                line += f" | effective_time={et}"
            if setid:
                line += f" | set_id={setid}"
            if dm:
                line += f" | {dm}"
            print(f"- {line}")

    ndc_results = out.get("openfda", {}).get("ndc_results")
    if ndc_results:
        print("\nopenFDA NDC matches")
        for r in ndc_results[:5]:
            brand = r.get("brand_name")
            generic = r.get("generic_name")
            product_ndc = r.get("product_ndc")
            # package_ndc is nested under packaging[]
            pkgs = r.get("packaging") or []
            pkg_ndcs = []
            if isinstance(pkgs, list):
                for p in pkgs[:3]:
                    if isinstance(p, dict) and p.get("package_ndc"):
                        pkg_ndcs.append(p.get("package_ndc"))
            pkg_str = ",".join(pkg_ndcs)
            print(f"- {brand or ''} / {generic or ''} | product_ndc={product_ndc} | package_ndc={pkg_str}")

    recalls = out.get("openfda", {}).get("recalls")
    if args.recalls and recalls:
        print("\nRecalls")
        if recalls.get("query"):
            print(f"- query: {recalls['query']}")
        for r in (recalls.get("results") or [])[: int(args.recalls_max)]:
            rn = r.get("recall_number")
            cls = r.get("classification")
            st = r.get("status")
            reason = _compact(r.get("reason_for_recall"), 220)
            print(f"- {rn} | {cls} | {st} | {reason}")

    shortages = out.get("openfda", {}).get("shortages")
    if args.shortages and shortages:
        print("\nShortages")
        if shortages.get("query"):
            print(f"- query: {shortages['query']}")
        for r in (shortages.get("results") or [])[: int(args.shortages_max)]:
            gn = r.get("generic_name")
            pres = _compact(r.get("presentation"), 180)
            st = r.get("status")
            print(f"- {st} | {gn} | {pres}")

    mpl_results = out.get("medlineplus", {}).get("results")
    if mpl_results:
        print("\nMedlinePlus")
        for r in mpl_results[:5]:
            t = (r or {}).get("title") or "(untitled)"
            u = (r or {}).get("url") or ""
            print(f"- {t}: {u}" if u else f"- {t}")

    # Keyword find results
    if label_obj and isinstance(label_obj, dict) and (label_obj.get("find") or {}).get("hits"):
        print("\nFind")
        hits = (label_obj.get("find") or {}).get("hits") or []
        for h in hits[: int(args.find_max) if getattr(args, 'find_max', None) else 20]:
            kw = h.get("keyword")
            field = h.get("field")
            snip = h.get("snippet")
            print(f"- {kw} [{field}]: {snip}")

    if args.print_url and URL_LOG:
        print("\nURLs")
        for u in URL_LOG:
            print(f"- {u}")

    if out.get("notes"):
        print("\nNotes")
        for n in out["notes"]:
            print(f"- {n}")

    if "error" in out:
        print(f"\nERROR: {out['error']}")

    return 0 if "error" not in out else 2


if __name__ == "__main__":
    raise SystemExit(main())
