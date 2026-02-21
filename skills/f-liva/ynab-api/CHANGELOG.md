# Changelog

## [2.1.0] - 2026-02-21

### ✨ Added

- 🚀 **One-Command Setup** (`setup-automation.sh`)
  - Interactive script to configure all cron jobs automatically
  - Creates 4 recommended automation jobs:
    - Daily Budget Check (7:15 AM)
    - Weekly Spending Review (Monday 8 AM)
    - Mid-Month Goal Check (15th at 9 AM)
    - Upcoming Bills Alert (10 AM daily)
  - Dry-run mode to preview changes
  - Validates YNAB configuration before setup
  - Prompts for WhatsApp number for delivery

### 📚 Improved

- Updated Quick Start guide to highlight one-command setup
- Added setup-automation.sh to all documentation
- Simplified onboarding process for new users

## [2.0.0] - 2026-02-21

### 🎉 Major Update - Complete Automation Suite

#### Added
- 📊 **Goal Progress Tracking** (`goals-progress.sh`)
  - Visual progress bars for all category goals
  - Color-coded status indicators (🟢🟡🔴)
  - Support for any month (current or historical)

- 📅 **Scheduled Transaction Alerts** (`scheduled-upcoming.sh`)
  - Lists upcoming bills and recurring payments
  - Customizable time window (default 7 days)
  - Total calculation for planning

- 📈 **Month Comparison** (`month-comparison.sh`)
  - Compare spending between any two months
  - Percentage change indicators
  - Trend arrows (⚠️↗️↘️✅)

- 🌅 **Daily Budget Check** (`daily-budget-check.sh`)
  - Comprehensive morning report
  - Age of Money status
  - Upcoming transactions (7 days)
  - Overspending alerts
  - Low-progress goals
  - Designed for cron automation

- 💸 **Real Transfer Support** (`transfer.sh`)
  - Uses `transfer_payee_id` for proper transfers
  - Automatically creates linked transactions
  - YNAB recognizes as true transfers

#### Fixed
- ⚠️ **CRITICAL**: Transfer transactions now use `transfer_payee_id` instead of `payee_name`
  - Previous method created unlinked transactions
  - New method creates properly linked transfer pairs
  - Updated documentation with correct implementation

#### Improved
- 📚 Complete documentation overhaul
- 🚀 Quick start guide for new users
- 🤖 Cron job setup examples
- 💡 Pro tips section
- 🔒 Security best practices
- 🆘 Comprehensive troubleshooting

#### Documentation
- Added `README.md` for quick reference
- Expanded `SKILL.md` with all features
- Added automation ideas and examples
- Included example outputs for all scripts

## [1.0.0] - 2026-02-21

### Initial Release

#### Added
- Basic YNAB API best practices
- Transaction categorization guidelines
- Milliunits handling
- Split transaction support
- Monthly expense calculation
- Account management
- Helper script (`ynab-helper.sh`)

---

**Upgrade Note**: Version 2.0.0 is a major update with breaking changes. If you have existing transfers created with `payee_name`, they won't be recognized as proper transfers. Consider recreating them using the new `transfer.sh` script.
