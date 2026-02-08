---
description: "Use when the user wants to convert markdown content into presentation slides. Generates an HTML slide deck using reveal.js or a simple standalone HTML presentation."
---

# Markdown Slides

Convert markdown into a self-contained HTML slide presentation.

## What This Does

Takes markdown content and generates a standalone HTML file that works as a slide deck in any browser.

## Usage

The user provides markdown content with slide separators (`---`) or asks to convert a markdown file into slides.

## Instructions

1. **Parse the markdown**: Split content on `---` (horizontal rule) to create individual slides.

2. **Generate HTML**: Create a self-contained HTML file using this template:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PRESENTATION_TITLE</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }
  .slide { width: 100vw; height: 100vh; display: none; flex-direction: column; justify-content: center; align-items: center; padding: 8vh 10vw; text-align: center; }
  .slide.active { display: flex; }
  .slide h1 { font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .slide h2 { font-size: 2.5rem; margin-bottom: 1rem; color: #667eea; }
  .slide p { font-size: 1.5rem; line-height: 1.8; max-width: 800px; color: #ccc; }
  .slide ul, .slide ol { font-size: 1.4rem; text-align: left; line-height: 2; }
  .slide code { background: #16213e; padding: 2px 8px; border-radius: 4px; font-size: 1.2rem; }
  .slide pre { background: #16213e; padding: 1.5rem; border-radius: 8px; text-align: left; overflow-x: auto; max-width: 90%; }
  .slide pre code { background: none; padding: 0; }
  .progress { position: fixed; bottom: 0; left: 0; height: 4px; background: #667eea; transition: width 0.3s; z-index: 10; }
  .slide-num { position: fixed; bottom: 12px; right: 20px; font-size: 0.9rem; color: #555; }
  .slide img { max-width: 70%; max-height: 60vh; border-radius: 8px; }
</style>
</head>
<body>
<!-- SLIDES_HERE -->
<div class="progress" id="progress"></div>
<div class="slide-num" id="slideNum"></div>
<script>
let current = 0;
const slides = document.querySelectorAll('.slide');
function show(n) {
  current = Math.max(0, Math.min(n, slides.length - 1));
  slides.forEach(s => s.classList.remove('active'));
  slides[current].classList.add('active');
  document.getElementById('progress').style.width = ((current + 1) / slides.length * 100) + '%';
  document.getElementById('slideNum').textContent = (current + 1) + ' / ' + slides.length;
}
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === ' ') show(current + 1);
  if (e.key === 'ArrowLeft') show(current - 1);
  if (e.key === 'Home') show(0);
  if (e.key === 'End') show(slides.length - 1);
});
document.addEventListener('click', e => {
  if (e.clientX > window.innerWidth / 2) show(current + 1);
  else show(current - 1);
});
show(0);
</script>
</body>
</html>
```

3. **Convert markdown to HTML** for each slide:
   - `# heading` → `<h1>`
   - `## heading` → `<h2>`
   - `- item` → `<ul><li>`
   - `**bold**` → `<strong>`
   - Code blocks → `<pre><code>`
   - Images → `<img>`
   - Paragraphs → `<p>`

4. **Save** as `slides.html` in the user's specified location.

5. **Usage instructions**: Tell the user to open the HTML file in a browser. Arrow keys or click to navigate. Press F11 for fullscreen.

## Notes
- Zero dependencies — single HTML file, works offline
- No API keys, no build tools, no npm install
- Keyboard navigation: ←/→ arrows, Space, Home/End
- Click left/right halves of screen to navigate
- Works great for quick presentations, demos, and talks
