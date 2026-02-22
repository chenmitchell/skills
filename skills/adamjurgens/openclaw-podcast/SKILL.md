---
name: openclaw-podcast
description: Transform your OpenClaw workspace into personalized AI-powered podcast briefings. Get daily audio updates on your work, priorities, and strategy in 8 compelling styles—from documentary narrator to strategic advisor. Connects directly to your agent's memory and files. Includes 3 free hours of podcast generation with your Superlore.ai API key. Schedule morning, midday, or evening briefings that keep you informed without reading screens.
metadata:
  openclaw:
    requires:
      env:
        - name: SUPERLORE_API_KEY
          description: "API key from superlore.ai — get one free at https://superlore.ai or use the setup wizard's email OTP flow"
          required: true
    permissions:
      - network: "HTTPS requests to superlore-api.onrender.com (official Superlore API hosted on Render)"
      - filesystem: "Reads workspace files (memory/*.md, JOBS.md, HEARTBEAT.md, MEMORY.md). Setup wizard optionally appends env var to ~/.zshrc or ~/.bashrc (user-confirmed)."
      - cron: "Setup wizard outputs openclaw cron commands for scheduling. Runs them only with explicit user confirmation."
---

# openclaw-podcast

**Generate personalized daily podcast briefings from your OpenClaw agent's memory.**

Your AI agent already knows what you did today — your memory files, project status, metrics, and decisions. This skill turns that context into a professional podcast briefing via [Superlore.ai](https://superlore.ai). Zero manual input required.

**Includes 3 free hours of podcast generation with your API key.**

## Setup

The fastest way to get started is the **setup wizard** — no API key required upfront:

```bash
node scripts/setup-crons.js
```

The wizard walks you through 7 steps and handles everything, including account creation via email:

1. **Connect Your Account** — sign up or log in with just your email (6-digit code sent to your inbox), or paste an existing API key
2. **Choose your styles** — pick from 8 built-in briefing styles
3. **Custom style** — optionally design your own briefing with a custom focus, tone, and voice
4. **Music bed** — choose ambient background music or voice-only
5. **Schedule** — set a time for each style (morning/midday/evening/weekly/custom cron)
6. **Preview episode** — generates a real episode so you can hear the quality immediately
7. **Activate** — outputs `openclaw cron add` commands; optionally runs them for you

**Already have an API key?** The wizard supports that too — just choose "Option A" when prompted to paste your existing key.

**Manual setup (optional alternative):**

If you'd rather skip the wizard and set things up manually:

1. Sign up at [superlore.ai](https://superlore.ai) and go to Account → API Keys
2. Set the environment variable:
   ```bash
   export SUPERLORE_API_KEY=your-api-key-here
   ```
   Add this to your `~/.zshrc` or `~/.bashrc` to persist across sessions.

## Quick Start

```bash
# Run the setup wizard (recommended — handles account + scheduling)
node scripts/setup-crons.js

# Or jump straight to generating a briefing if you already have an API key
node scripts/generate-episode.js

# Try different styles
node scripts/generate-episode.js --style "The Advisor"
node scripts/generate-episode.js --style "10X Thinking"

# Preview the prompt without creating an episode
node scripts/generate-episode.js --dry-run
```

## First Episode in 60 Seconds

The fastest path to your first briefing is the setup wizard:

```bash
node scripts/setup-crons.js
# → Enter your email
# → Check inbox for 6-digit code
# → Paste the code — your API key is created automatically
# → Wizard generates a preview episode so you can hear the quality
```

Or, if you already have an API key:

```bash
export SUPERLORE_API_KEY=your-key-here
node scripts/generate-episode.js --dry-run    # Preview what gets sent
node scripts/generate-episode.js              # Generate your first episode!
```

Your episode will be ready in ~2 minutes at the URL printed in the output. That's it — your agent just turned today's work into a podcast.

## What It Does

The skill reads your OpenClaw workspace files:
- `memory/YYYY-MM-DD.md` — Daily activity logs
- `JOBS.md` — Project status and job board
- `HEARTBEAT.md` — Current priorities and upcoming work
- `MEMORY.md` — Long-term context (optional)

It then pre-processes this data into a structured briefing (accomplishments, metrics, blockers, upcoming work) and generates a professional podcast episode using Superlore's API.

## Privacy & Data Flow

Your workspace contains sensitive information. Here's exactly how this skill protects it:

### What happens when you generate a briefing

```
Your Machine (private)              Superlore API (remote)
┌─────────────────────┐             ┌──────────────────┐
│ 1. Agent reads your │             │                  │
│    workspace files  │             │ 4. GPT writes    │
│                     │             │    podcast script │
│ 2. Script extracts  │             │                  │
│    work summaries   │   ONLY      │ 5. Kokoro TTS    │
│                     │  ──────►    │    generates      │
│ 3. Secrets stripped │  briefing   │    audio          │
│    (keys, emails,   │   text      │                  │
│    IPs, paths, DBs) │             │ 6. Private episode│
│                     │             │    stored         │
└─────────────────────┘             └──────────────────┘
```

### What IS sent
- A processed briefing summary (~3,000 chars of work narrative)
- Style instructions (e.g., "be a documentary narrator")
- Voice/speed preferences

### What is NEVER sent
- ❌ Your raw workspace files
- ❌ API keys, tokens, passwords, or credentials
- ❌ Email addresses
- ❌ IP addresses or internal hostnames
- ❌ Database connection strings
- ❌ File paths from your system
- ❌ SSH credentials
- ❌ Agent configuration (model routing, cron schedules, etc.)

### How secrets are stripped

The script applies **three layers of sanitization**:

1. **Section filtering** — Entire sections of MEMORY.md that contain operational details (credentials, model routing, cron configs) are excluded before any data extraction.

2. **Line filtering** — Individual lines mentioning API keys, passwords, tokens, database URLs, or service IDs are dropped.

3. **Pattern stripping** — A final regex pass on the entire briefing catches anything that looks like a secret: long tokens (`sk_*`, `ghp_*`, `rpa_*`), database URLs (`postgres://`), email addresses, internal IPs, base64 blobs, and absolute file paths.

### Verify it yourself

Run `--dry-run` to see **exactly** what would be sent to Superlore — nothing hidden:

```bash
node scripts/generate-episode.js --dry-run
```

This prints the complete prompt. If you see anything sensitive, [report it](https://github.com/openclaw/openclaw/issues) so we can improve the sanitization rules.

### Episode visibility

All briefing episodes are created with `visibility: private`. This is **hardcoded** in the script and cannot be overridden by flags or configuration. Only you can access your briefings.

### What Superlore sees

Superlore's API receives the briefing text, processes it through GPT (for script writing) and Kokoro TTS (for audio). The episode is stored on Superlore's infrastructure as a private episode tied to your account. Superlore does not have access to your filesystem, your OpenClaw agent, or any files beyond the briefing text you send.

## Briefing Styles

Choose from 8 compelling perspectives—each designed to give you a different lens on your work:

1. **The Briefing** — Your personal documentary. A professional narrator walks through your day's accomplishments, key metrics, obstacles, and what's coming next. Clear, structured, and comprehensive.

2. **Opportunities & Tactics** — Spot what you're missing. This style hunts for growth opportunities, strategic angles, and tactical moves hiding in your daily work. Perfect when you need fresh ideas.

3. **10X Thinking** — Break through limits. A moonshot advisor challenges your assumptions, questions your approach, and pushes you to think 10x bigger. Use when you feel stuck in incremental thinking.

4. **The Advisor** — Honest feedback from a seasoned mentor. No sugar-coating—just direct guidance on what's working, what's not, and what to do about it. Your trusted counsel.

5. **Focus & Priorities** — Cut through the noise. Ruthlessly identifies what actually matters and what's just busywork. Helps you say no to distractions and double down on leverage.

6. **Growth & Scale** — All about the numbers. Revenue, users, conversion funnels, and growth loops. Analyzes your work through the lens of business metrics and scalability.

7. **Week in Review** — Step back and see patterns. Synthesizes your week into trends, lessons learned, and clear goals for the week ahead. Best on Friday or Sunday evenings.

8. **The Futurist** — Connect today to tomorrow. Ties your daily work to your 3, 6, and 12-month vision. Keeps you aligned with long-term goals while moving fast.

See `references/styles.md` for full style definitions and prompt templates.

## Voices

Three curated voices are available for your briefings:

| Voice | Character | Best For |
|-------|-----------|----------|
| **Luna** (`af_heart-80_af_sarah-15_af_nicole-5`) | Warm, balanced — female | The Briefing, The Advisor, Week in Review |
| **Michael** (`am_michael-60_am_eric-40`) | Rich, resonant — male blend | Opportunities, 10X Thinking, Growth & Scale |
| **Heart** (`af_heart`) | Soft, intimate — female | Focus & Priorities, The Futurist |

Luna is Superlore's signature voice — a carefully balanced blend that sounds natural across a wide range of content. Michael brings authority to strategic and growth-focused styles. Heart is the most personal of the three, ideal for styles that speak directly to the individual.

## Custom Styles

Not limited to the 8 defaults! Create your own podcast style by dropping a JSON file in your workspace's `podcast-styles/` directory:

```json
// podcast-styles/my-style.json
{
  "name": "My Custom Style",
  "description": "Brief description",
  "voice": "af_heart-80_af_sarah-15_af_nicole-5",
  "speed": 0.95,
  "targetMinutes": 6,
  "instructions": "Detailed instructions for the AI narrator..."
}
```

Voice options for custom styles:
- `"af_heart-80_af_sarah-15_af_nicole-5"` — **Luna** (warm, balanced)
- `"am_michael-60_am_eric-40"` — **Michael** (rich, authoritative)
- `"af_heart"` — **Heart** (soft, intimate)

Then use it:
```bash
node scripts/generate-episode.js --style "My Custom Style"
node scripts/generate-episode.js --custom "my-style"  # matches filename
node scripts/generate-episode.js --list-styles  # see all available
```

Two example custom styles are included: **Founder Debrief** (casual co-founder conversation) and **Competitor Watch** (competitive intelligence lens).

## Scheduling

Use `setup-crons.js` to configure automatic daily briefings:

```bash
node scripts/setup-crons.js
```

The setup wizard guides you through 7 steps:

1. **Connect Your Account** — Sign up or log in via email OTP (6-digit code), or paste an existing API key; validates key and shows remaining hours
2. **Choose your styles** — Pick from the 8 built-in styles (e.g., "The Briefing" mornings, "The Advisor" evenings)
3. **Custom style** — Optionally design your own briefing with a custom focus, tone, and voice
4. **Music bed** — Choose ambient background music or voice-only
5. **Schedule** — Set a time for each style (morning/midday/evening/weekly/custom cron)
6. **Preview episode** — Generates a real episode so you can hear the quality immediately
7. **Activate** — Outputs `openclaw cron add` commands; optionally runs them for you

Each built-in style has a curated default voice:
- **Luna** voices: The Briefing, The Advisor, Week in Review
- **Michael** voices: Opportunities & Tactics, 10X Thinking, Growth & Scale
- **Heart** voices: Focus & Priorities, The Futurist

Example output:
```bash
# The script will generate commands like:
/cron create "0 8 * * *" agent:run node scripts/generate-episode.js --style "The Briefing" --time-of-day morning

# Just copy-paste these into your OpenClaw chat to activate
```

Once scheduled, your briefings will generate automatically and be ready to listen at your chosen times. You'll receive notifications with episode links.

## Configuration

The script uses sensible defaults but accepts these parameters:

- `--style <name>` — Briefing style (default: "The Briefing")
- `--time-of-day <morning|midday|evening>` — Affects greeting and tone
- `--date YYYY-MM-DD` — Generate for a specific date (default: today)
- `--dry-run` — **Preview exactly what would be sent** (nothing hidden)
- `--no-memory` — Skip MEMORY.md entirely (only use daily files)
- `--api-url <url>` — Override Superlore API URL
- `--device-id <id>` — Optional device identifier for usage analytics (not required for authentication)
- `--channel <channel>` — Deliver the episode link to a specific channel (e.g., telegram, discord) when the episode is ready

## Requirements

- OpenClaw workspace with memory files
- Superlore.ai API key (get yours at [superlore.ai](https://superlore.ai))
- Internet connection (episodes created via Superlore API)
- **3 free hours of podcast generation included** with your API key

## Learn More

- **Superlore.ai** — [https://superlore.ai](https://superlore.ai)
- **API Reference** — `references/api.md`
- **Style Guide** — `references/styles.md`

## Tips

- Start with **"The Briefing"** style to get a feel for the format
- Use **"The Advisor"** when you want honest feedback on your work
- Try **"10X Thinking"** when you feel stuck or want to challenge assumptions
- **"Week in Review"** works best on Friday or Sunday evenings
- Use `--dry-run` to experiment with prompts before creating episodes
- Morning briefings focus on the day ahead; evening briefings review accomplishments

## Examples

```bash
# Morning briefing with advisor style
node scripts/generate-episode.js --style "The Advisor" --time-of-day morning

# Weekly review for Friday
node scripts/generate-episode.js --style "Week in Review" --time-of-day evening

# Preview what a growth-focused briefing would look like
node scripts/generate-episode.js --style "Growth & Scale" --dry-run

# Generate and deliver the episode link to Telegram when ready
node scripts/generate-episode.js --channel telegram
```

---

**Made with ❤️ for the OpenClaw community. Powered by Superlore.ai.**
