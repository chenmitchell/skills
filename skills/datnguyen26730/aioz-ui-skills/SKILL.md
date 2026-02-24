---
name: aioz-ui-v2
description: Build UI components and pages using AIOZ UI V2 design system. Use this skill whenever the user wants to create, edit, or style React components using AIOZ UI tokens, Tailwind classes, color tokens, typography utilities, or icons from @aioz-ui/icon-react. Trigger on any task involving AIOZ UI components, design tokens like --sf-neu-block or --text-neu-bold, brand colors, typography classes (text-title-01, text-body-02), or icon imports. Also use when translating Figma MCP output (fill tokens, typography styles, icon layer names) into production-ready AIOZ UI V2 code.
---

# AIOZ UI V2 — Component Development Skill

This skill helps you build production-quality React components using the AIOZ UI V2 design system, including correct color tokens, typography utilities, icon imports, and component patterns.

## Quick Reference Files

Load these reference files from the `references/` folder as needed:

| File                             | When to read it                                                         |
| -------------------------------- | ----------------------------------------------------------------------- |
| `references/colors.md`           | Mapping Figma fill/stroke/text tokens → Tailwind bg/text/border classes |
| `references/typography.md`       | Mapping Figma typography styles → Tailwind text-\* classes              |
| `references/icons.md`            | Finding icon names, imports from `@aioz-ui/icon-react`                  |
| `references/using-components.md` | Component API reference: Button, Input, Table, Badge, Modal, etc.       |

**Always read the relevant reference file before writing code.** Token names and class names are design-system-specific and must not be guessed.

---

## Core Principles

### 1. Token-first, never raw Tailwind

- ❌ `text-sm text-gray-500 bg-white border-gray-200`
- ✅ `text-body-02 text-subtitle-neutral bg-sf-screen border-border-neutral`

### 2. Typography utilities are all-in-one

Each `text-*` utility from `tw-inline.css` already bakes in font-size, line-height, weight, and font-family. **Never** stack `font-medium`, `text-sm`, etc. on top.

### 3. Use component primitives over custom divs

Prefer `<Button>`, `<Input>`, `<Badge>` from `@aioz-ui/core-v2/components` over hand-rolled elements where applicable.

### 4. Icons always via `@aioz-ui/icon-react`

Never use emoji, SVG literals, or other icon libraries. Color icons via `className="text-icon-neutral"` (currentColor inheritance).

---

## Figma MCP → Code Workflow

When translating Figma MCP output:

1. **Fill/color tokens** → open `references/colors.md` → find token in table → use Tailwind class
2. **Typography style** (e.g. `Subheadline/02`) → open `references/typography.md` → map to class
3. **Icon layer name** (e.g. `icon/24px/outline/wallet-01`) → strip prefix → PascalCase → append `Icon` → `Wallet01Icon`
4. **Component type** → open `references/using-components.md` → use the correct component API

---

## File & Import Conventions

```tsx
// Design system components
import { Button, Input, Badge, Table } from '@aioz-ui/core-v2/components'

// Icons (always named imports, PascalCase + "Icon" suffix)
import { Search01Icon, Plus01Icon, Wallet01Icon } from '@aioz-ui/icon-react'

// Styles (ensure tw-inline.css is loaded in the project)
// Classes like text-title-01, bg-sf-neutral, border-border-neutral come from tw-inline.css
```

---

## Common Layout Patterns

```tsx
// Page shell
<div className="min-h-screen bg-sf-screen">
  <main className="p-6">...</main>
</div>

// Card / panel
<div className="bg-sf-object border border-border-neutral rounded-2xl p-6">

// Sidebar / nav block
<nav className="bg-sf-neutral-block border-r border-border-neutral h-full">

// Active nav item
<div className="bg-sf-neutral text-onsf-text-neutral rounded-lg px-3 py-2">

// Section heading
<h2 className="text-title-03 text-title-neutral">Section Title</h2>

// Body description
<p className="text-body-02 text-subtitle-neutral">Supporting description text.</p>
```

---

## Status Badge Patterns

```tsx
// Success
<span className="bg-sf-success-sec text-onsf-text-success border border-border-success rounded-full px-2 py-0.5 text-body-03">
  Active
</span>

// Error
<span className="bg-sf-error-sec text-onsf-text-error border border-border-error rounded-full px-2 py-0.5 text-body-03">
  Rejected
</span>

// Warning
<span className="bg-sf-warning-sec text-onsf-text-warning border border-border-warning rounded-full px-2 py-0.5 text-body-03">
  Pending
</span>

// Info
<span className="bg-sf-info-sec text-onsf-text-info border border-border-info rounded-full px-2 py-0.5 text-body-03">
  Review
</span>
```

---

## Icon Usage

```tsx
// Standard icon in nav/body
<Search01Icon size={16} className="text-icon-neutral" />

// Icon button (view action)
<button className="w-8 h-8 rounded-lg border border-border-neutral flex items-center justify-center text-icon-neutral hover:bg-sf-neutral hover:text-title-neutral transition-colors">
  <EyeOpenIcon size={16} />
</button>

// Destructive icon button
<button className="w-8 h-8 rounded-lg border border-border-error flex items-center justify-center text-onsf-text-error hover:bg-sf-error-sec transition-colors">
  <Trash01Icon size={16} />
</button>
```

---

## Checklist Before Submitting Code

- [ ] All colors use design token classes (no raw Tailwind colors)
- [ ] All typography uses `text-*` token classes (no `text-sm`, `font-medium`, etc.)
- [ ] All icons imported from `@aioz-ui/icon-react` with `Icon` suffix
- [ ] Interactive elements have hover/focus/disabled states using token classes
- [ ] Component primitives used where applicable (Button, Input, Badge, Table)
