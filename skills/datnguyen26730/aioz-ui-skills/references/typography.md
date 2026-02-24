---
name: aioz-ui-typography
description: Typography utility reference for AIOZ UI V2 with Tailwind CSS v4.
---

# AIOZ UI V2 – Typography Reference

Each utility bakes in font-size + line-height + font-weight + font-family. **Never** add manual font-size overrides on top.

## Font Families

| Token                | Value                            |
| -------------------- | -------------------------------- |
| `font-neue`          | PP Neue Montreal (default)       |
| `font-formula`       | PP Formula (display titles only) |
| `font-fraktion-mono` | PP Fraktion Mono (code/mono)     |

## Titles (500 Medium)

| Class           | Size | Figma Name |
| --------------- | ---- | ---------- |
| `text-title-01` | 32px | `Title/01` |
| `text-title-02` | 24px | `Title/02` |
| `text-title-03` | 20px | `Title/03` |
| `text-title-04` | 18px | `Title/04` |

## Subheadlines (500 Medium)

| Class                 | Size | Figma Name       |
| --------------------- | ---- | ---------------- |
| `text-subheadline-01` | 16px | `Subheadline/01` |
| `text-subheadline-02` | 14px | `Subheadline/02` |
| `text-subheadline-03` | 12px | `Subheadline/03` |

## Body (400 Regular)

| Class          | Size | Figma Name |
| -------------- | ---- | ---------- |
| `text-body-00` | 20px | `Body/00`  |
| `text-body-01` | 16px | `Body/01`  |
| `text-body-02` | 14px | `Body/02`  |
| `text-body-03` | 12px | `Body/03`  |

## Body Links (500 Medium — same size as Body but bolder)

| Class               | Size |
| ------------------- | ---- |
| `text-body-00-link` | 20px |
| `text-body-01-link` | 16px |
| `text-body-02-link` | 14px |
| `text-body-03-link` | 12px |

## Caption

| Class               | Size |
| ------------------- | ---- |
| `text-caption`      | 10px |
| `text-caption-link` | 10px |

## Button Labels (500 Medium)

| Class                 | Size       |
| --------------------- | ---------- |
| `text-button-00`      | 16px       |
| `text-button-01`      | 14px       |
| `text-button-02`      | 12px       |
| `text-bold-button-00` | 16px (700) |
| `text-bold-button-01` | 14px (700) |
| `text-bold-button-02` | 12px (700) |

## Mono (PP Fraktion Mono, 400)

| Class          | Size |
| -------------- | ---- |
| `text-mono-01` | 14px |
| `text-mono-02` | 12px |

## Figma MCP → Tailwind Mapping

| Figma MCP Style  | Tailwind Class        |
| ---------------- | --------------------- |
| `Title/01`       | `text-title-01`       |
| `Title/02`       | `text-title-02`       |
| `Title/03`       | `text-title-03`       |
| `Title/04`       | `text-title-04`       |
| `Subheadline/01` | `text-subheadline-01` |
| `Subheadline/02` | `text-subheadline-02` |
| `Subheadline/03` | `text-subheadline-03` |
| `Body/00`        | `text-body-00`        |
| `Body/01`        | `text-body-01`        |
| `Body/02`        | `text-body-02`        |
| `Body/03`        | `text-body-03`        |
| `Body/00 Link`   | `text-body-00-link`   |
| `Body/01 Link`   | `text-body-01-link`   |
| `Body/02 Link`   | `text-body-02-link`   |
| `Body/03 Link`   | `text-body-03-link`   |
| `Caption`        | `text-caption`        |
| `Caption Link`   | `text-caption-link`   |
| `Button/00`      | `text-button-00`      |
| `Button/01`      | `text-button-01`      |
| `Button/02`      | `text-button-02`      |
| `Mono/01`        | `text-mono-01`        |
| `Mono/02`        | `text-mono-02`        |

## Size Heuristic (when Figma gives px without name)

| px   | Regular         | Medium/Bold           |
| ---- | --------------- | --------------------- |
| 32px | `text-title-01` | `text-title-01`       |
| 24px | `text-title-02` | `text-title-02`       |
| 20px | `text-body-00`  | `text-title-03`       |
| 18px | —               | `text-title-04`       |
| 16px | `text-body-01`  | `text-subheadline-01` |
| 14px | `text-body-02`  | `text-subheadline-02` |
| 12px | `text-body-03`  | `text-subheadline-03` |
| 10px | `text-caption`  | `text-caption-link`   |

## Anti-Patterns

```tsx
// ❌ Wrong
<h2 className="text-title-03 text-xl font-semibold">
<p className="text-sm text-gray-500">
<span className="text-subheadline-02 font-medium">

// ✅ Correct
<h2 className="text-title-03 text-title-neutral">
<p className="text-body-02 text-subtitle-neutral">
<span className="text-subheadline-02 text-subtitle-neutral">
```
