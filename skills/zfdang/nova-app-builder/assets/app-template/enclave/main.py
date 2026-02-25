"""
Nova App Template — replace this with your app logic.

Required endpoints:
  GET /                        — health check (returns enclave address)
  POST /.well-known/attestation — raw CBOR attestation (Nova registry)

Usage of odyn:
  IN_ENCLAVE=true  → uses localhost:18000 (TEE)
  IN_ENCLAVE=false → uses mock at odyn.sparsity.cloud:18000 (local dev)
"""
import base64
from fastapi import FastAPI, HTTPException, Response
from odyn import Odyn

app = FastAPI(title="Nova App", version="1.0.0")
odyn = Odyn()


@app.get("/")
def health():
    return {
        "status": "ok",
        "enclave": odyn.eth_address(),
    }


@app.get("/api/sign")
def sign_example(message: str = "hello"):
    """Sign an arbitrary message with the enclave key."""
    try:
        result = odyn.sign_message(message)
        return result  # {"signature": "0x...", "address": "0x..."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/attestation")
def get_attestation():
    """Base64-encoded Nitro attestation document."""
    try:
        cbor_bytes = odyn.get_attestation()
        return {"attestation": base64.b64encode(cbor_bytes).decode()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/.well-known/attestation")
def attestation_cbor():
    """Raw CBOR attestation — required by Nova App Registry."""
    try:
        cbor_bytes = odyn.get_attestation()
        return Response(content=cbor_bytes, media_type="application/cbor")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
