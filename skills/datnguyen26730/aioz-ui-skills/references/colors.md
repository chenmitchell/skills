---
name: aioz-ui-colors
description: Color token mapping for AIOZ UI V2. Maps Figma MCP component token names (e.g. --text-neu-bold, --sf-neu-block, --onsf-suc-default) to Tailwind CSS utility classes from tw-inline.css. Use this whenever the Figma MCP returns a color/fill token and you need the correct Tailwind class to apply.
---

# AIOZ UI V2 – Color Token → Tailwind Class Reference

**How to use:** When Figma MCP returns a fill, stroke, or text color token name, find it in the table below and use the corresponding Tailwind class.

---

## Text Colors

| Figma Token            | Tailwind Class            | Use For                             |
| ---------------------- | ------------------------- | ----------------------------------- |
| `--text-neu-bold`      | `text-title-neutral`      | Primary text, headings, bold labels |
| `--text-neu-pri`       | `text-title-neutral`      | Primary body text, titles           |
| `--text-neu-body`      | `text-text-neutral-body`  | Regular body copy                   |
| `--text-neu-mute`      | `text-content-sec`        | Muted / helper text                 |
| `--text-neu-white`     | `text-white`              | Fixed white text (always white)     |
| `--text-brand-on-item` | `text-text-brand-on-item` | Brand text placed on a colored item |

---

## On-Surface Text (text ON a colored surface)

| Figma Token              | Tailwind Class                          | Use For                                 |
| ------------------------ | --------------------------------------- | --------------------------------------- |
| `--onsf-neu-default`     | `text-onsf-text-neutral`                | Text on neutral/grey surface            |
| `--onsf-neu-hover`       | `text-onsf-text-neutral-hover`          | Text on neutral surface, hover state    |
| `--onsf-neu-grey`        | `text-onsf-text-neutral-grey`           | Grey text on neutral surface            |
| `--onsf-neu-pressed`     | `text-onsf-text-neutral-pressed`        | Text on neutral surface, pressed state  |
| `--onsf-neu-focus`       | `text-onsf-text-neutral-focus`          | Text on neutral surface, focus state    |
| `--onsf-suc-default`     | `text-onsf-text-success`                | Text on success (green) surface         |
| `--onsf-suc-hover`       | `text-onsf-text-success-hover`          | Text on success surface, hover          |
| `--onsf-error-default`   | `text-onsf-text-error`                  | Text on error (red) surface             |
| `--onsf-error-hover`     | `text-onsf-text-error-hover`            | Text on error surface, hover            |
| `--onsf-error-pressed`   | `text-onsf-text-error-pressed`          | Text on error surface, pressed          |
| `--onsf-error-focus`     | `text-onsf-text-error-focus`            | Text on error surface, focus            |
| `--onsf-warn-default`    | `text-onsf-text-warning`                | Text on warning (orange) surface        |
| `--onsf-info-default`    | `text-onsf-text-info`                   | Text on info (blue) surface             |
| `--onsf-bra-default`     | `text-onsf-text-pri`                    | Text on brand/primary surface           |
| `--onsf-fix-color-white` | `text-white`                            | Fixed white (always white, both themes) |
| `--onsf-fix-color-neu`   | `text-onsf-text-neutral-fix-on-neutral` | Fixed dark neutral (always dark)        |
| `--onsf-fix-color-pri`   | `text-onsf-text-pri-dark`               | Fixed primary brand text                |
| `--onsf-disable-disable` | `text-onsf-text-disable`                | Disabled state text                     |

---

## Surface / Background Colors

| Figma Token               | Tailwind Class            | Use For                                            |
| ------------------------- | ------------------------- | -------------------------------------------------- |
| `--background-bg-screen`  | `bg-sf-screen`            | Page / screen background                           |
| `--sf-neu-block`          | `bg-sf-neutral-block`     | Sidebar, navigation block, panels                  |
| `--sf-neu-default`        | `bg-sf-neutral`           | Hover state, active nav item, row highlight        |
| `--sf-neu-light-hover`    | `bg-sf-neutral-light`     | Light neutral hover (slightly darker than neutral) |
| `--sf-neu-hover`          | `bg-sf-neutral-hover`     | Neutral pressed / strong hover                     |
| `--sf-pri-pri`            | `bg-sf-pri`               | Primary brand fill (green button bg)               |
| `--sf-pri-pri-hover`      | `bg-sf-pri-hover`         | Primary hover state                                |
| `--sf-pri-pri-pressed`    | `bg-sf-pri-pressed`       | Primary pressed state                              |
| `--sf-pri-sec-default`    | `bg-sf-sec`               | Secondary brand tint (light green bg)              |
| `--sf-pri-sec-hover`      | `bg-sf-sec-hover`         | Secondary brand hover                              |
| `--sf-pri-sec-pressed`    | `bg-sf-sec-pressed`       | Secondary brand pressed                            |
| `--sf-pri-sec-focus`      | `bg-sf-sec-focus`         | Secondary brand focus                              |
| `--sf-suc-pri-default`    | `bg-sf-success-pri`       | Success fill (solid green)                         |
| `--sf-suc-pri-hover`      | `bg-sf-success-pri-hover` | Success hover                                      |
| `--sf-suc-sec-default`    | `bg-sf-success-sec`       | Success tint background                            |
| `--sf-error-sec-default`  | `bg-sf-error-sec`         | Error tint background                              |
| `--sf-error-sec-hover`    | `bg-sf-error-sec-hover`   | Error tint hover                                   |
| `--sf-error-sec-pressed`  | `bg-sf-error-sec-pressed` | Error tint pressed                                 |
| `--sf-error-sec-focus`    | `bg-sf-error-sec-focus`   | Error tint focus                                   |
| `--sf-info-sec-default`   | `bg-sf-info-sec`          | Info tint background                               |
| `--sf-warn-sec-default`   | `bg-sf-warning-sec`       | Warning tint background                            |
| `--sf-disable-sf-disable` | `bg-sf-disable`           | Disabled surface                                   |

---

## Border Colors

| Figma Token                | Tailwind Class                     | Use For                                  |
| -------------------------- | ---------------------------------- | ---------------------------------------- |
| `--border-neu-default`     | `border-border-neutral`            | Default border (inputs, cards, dividers) |
| `--border-neu-grey`        | `border-border-neutral-grey`       | Stronger neutral border                  |
| `--border-neu-light-grey`  | `border-border-neutral-light-grey` | Very subtle border                       |
| `--border-neu-black`       | `border-border-neutral-grey`       | Darkest neutral border (maps to grey)    |
| `--border-pri-default`     | `border-border-pri`                | Primary/focus ring                       |
| `--border-pri-hover`       | `border-border-pri-hover`          | Primary border hover                     |
| `--border-pri-pri-focus`   | `border-border-pri-focus`          | Primary border focus                     |
| `--border-suc-default`     | `border-border-success`            | Success state border                     |
| `--border-error-default`   | `border-border-error`              | Error state border                       |
| `--border-error-hover`     | `border-border-error-hover`        | Error border hover                       |
| `--border-info-default`    | `border-border-info`               | Info state border                        |
| `--border-warn-default`    | `border-border-warning`            | Warning state border                     |
| `--border-disable-disable` | `border-border-disable`            | Disabled border                          |

---

## Complete Tailwind Inline Color Reference

All classes available from `tw-inline.css`. Use these directly in className without needing to trace through component tokens.

### Text

```
text-title-neutral       — Primary heading / title text
text-subtitle-neutral    — Secondary label / subtitle
text-content-sec         — Muted / secondary body copy
text-icon-neutral        — Icon color (same hue as title-neutral)
text-text-neutral-body   — Regular body paragraph text
text-text-brand          — Brand (primary green) colored text
text-text-brand-on-item  — Brand text on a highlighted item
text-text-success        — Success green text
text-text-warning        — Warning orange text
text-text-error          — Error red text
text-text-info           — Info blue text
text-text-disable        — Disabled text
text-main-caption        — Caption / fine print
text-object-accent       — Brand accent (links, interactive emphasis)
text-object-accent-hover — Brand accent hover
```

### On-Surface Text (for text placed on a colored `bg-sf-*` surface)

```
text-onsf-text-neutral              — On neutral surface
text-onsf-text-neutral-hover        — On neutral surface, hover
text-onsf-text-neutral-pressed      — On neutral surface, pressed
text-onsf-text-neutral-focus        — On neutral surface, focus
text-onsf-text-neutral-grey         — Grey text on neutral surface
text-onsf-text-neutral-lightgrey    — Light grey text on neutral surface
text-onsf-text-neutral-fix-on-neutral — Fixed dark text (always dark regardless of theme)
text-onsf-text-pri                  — On primary surface
text-onsf-text-pri-dark             — Dark variant on primary surface
text-onsf-text-brand-fix-on-sec     — Brand text on secondary surface
text-onsf-text-success              — On success surface
text-onsf-text-success-hover        — On success surface, hover
text-onsf-text-warning              — On warning surface
text-onsf-text-error                — On error surface
text-onsf-text-error-hover          — On error surface, hover
text-onsf-text-info                 — On info surface
text-onsf-text-disable              — On disabled surface
```

### Background / Surface

```
bg-sf-screen             — Page background (lightest)
bg-sf-muted              — Muted background
bg-sf-object             — Card / panel / raised surface
bg-sf-neutral-block      — Sidebar / nav container
bg-sf-neutral            — Hover bg, active nav item
bg-sf-neutral-light      — Slightly darker neutral
bg-sf-neutral-hover      — Neutral pressed / strong hover
bg-sf-neutral-pressed    — Neutral pressed
bg-sf-neutral-focus      — Neutral focus
bg-sf-pri                — Primary brand fill
bg-sf-pri-hover          — Primary hover
bg-sf-pri-focus          — Primary focus
bg-sf-pri-pressed        — Primary pressed
bg-sf-sec                — Secondary brand tint
bg-sf-sec-hover          — Secondary hover
bg-sf-sec-focus          — Secondary focus
bg-sf-sec-pressed        — Secondary pressed
bg-sf-success-pri        — Success primary fill
bg-sf-success-pri-hover  — Success hover
bg-sf-success-sec        — Success tint
bg-sf-warning-pri        — Warning primary fill
bg-sf-warning-sec        — Warning tint
bg-sf-error-pri          — Error primary fill
bg-sf-error-sec          — Error tint
bg-sf-error-sec-hover    — Error tint hover
bg-sf-info-pri           — Info primary fill
bg-sf-info-sec           — Info tint
bg-sf-disable            — Disabled surface
```

### Border

```
border-border-neutral            — Default (inputs, cards, dividers)
border-border-neutral-light-grey — Very subtle
border-border-neutral-grey       — Medium neutral
border-border-neutral-pressed    — Pressed/active neutral
border-border-pri                — Primary / focus ring
border-border-pri-hover          — Primary hover
border-border-pri-pressed        — Primary pressed
border-border-pri-focus          — Primary focus
border-border-success            — Success
border-border-success-hover      — Success hover
border-border-warning            — Warning
border-border-error              — Error
border-border-error-hover        — Error hover
border-border-info               — Info
border-border-disable            — Disabled
```

---

## Common Component Patterns

```tsx
// Page shell
<div className="min-h-screen bg-sf-screen">

// Card
<div className="bg-sf-object border border-border-neutral rounded-2xl p-6">

// Sidebar nav block
<nav className="bg-sf-neutral-block border-r border-border-neutral">

// Active nav item
<div className="bg-sf-neutral text-onsf-text-neutral">

// Inactive nav item
<div className="text-subtitle-neutral hover:bg-sf-neutral hover:text-onsf-text-neutral">

// Primary button surface (prefer <Button variant="primary"> instead)
<div className="bg-sf-pri text-white">

// Secondary brand avatar / chip bg
<div className="bg-sf-sec text-onsf-text-pri">

// Status badge — Success
<span className="bg-sf-success-sec text-onsf-text-success border border-border-success">

// Status badge — Warning
<span className="bg-sf-warning-sec text-onsf-text-warning border border-border-warning">

// Status badge — Error
<span className="bg-sf-error-sec text-onsf-text-error border border-border-error">

// Status badge — Info
<span className="bg-sf-info-sec text-onsf-text-info border border-border-info">

// Brand link text
<a className="text-object-accent hover:text-object-accent-hover hover:underline">

// Disabled input
<div className="bg-sf-disable border-border-disable text-onsf-text-disable">

// Table header cell text
<th className="text-subheadline-02 text-subtitle-neutral">

// Table body cell — primary column
<td className="text-title-neutral font-medium">

// Table body cell — secondary column
<td className="text-text-neutral-body">

// Icon
<SomeIcon size={16} className="text-icon-neutral" />
```
