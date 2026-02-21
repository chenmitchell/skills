#!/bin/bash
# Show progress for all category goals in current month
# Usage: ./goals-progress.sh [month]  # default: current

set -e

# Load config
if [ -f ~/.config/ynab/config.json ]; then
  API_KEY=$(jq -r '.api_key' ~/.config/ynab/config.json)
  BUDGET_ID=$(jq -r '.budget_id // "last-used"' ~/.config/ynab/config.json)
elif [ -f /home/node/clawd/config/ynab.json ]; then
  API_KEY=$(jq -r '.api_key' /home/node/clawd/config/ynab.json)
  BUDGET_ID="${YNAB_BUDGET_ID:-last-used}"
else
  echo "Error: YNAB config not found" >&2
  exit 1
fi

MONTH="${1:-current}"
YNAB_API="https://api.ynab.com/v1"

# Get month data
MONTH_DATA=$(curl -s "$YNAB_API/budgets/$BUDGET_ID/months/$MONTH" \
  -H "Authorization: Bearer $API_KEY")

# Check for errors
ERROR=$(echo "$MONTH_DATA" | jq -r '.error.detail // empty')
if [ -n "$ERROR" ]; then
  echo "Error: $ERROR" >&2
  exit 1
fi

# Get month name
MONTH_NAME=$(echo "$MONTH_DATA" | jq -r '.data.month.month')

echo "📊 PROGRESSI OBIETTIVI - $MONTH_NAME"
echo ""

# Process categories with goals
echo "$MONTH_DATA" | jq -r '
.data.month.categories[] 
| select(.goal_type != null and .deleted == false)
| . as $cat
| ($cat.activity / -1000) as $spent
| ($cat.goal_target / 1000) as $target
| if $target > 0 then ($spent / $target * 100) else 0 end as $pct
| if $pct > 100 then "🔴" elif $pct > 80 then "⚠️" elif $pct > 50 then "🟡" else "🟢" end as $icon
| ($pct / 10 | floor) as $filled
| (["█","█","█","█","█","█","█","█","█","█"] | .[0:$filled] | join("")) as $bar_filled
| (["░","░","░","░","░","░","░","░","░","░"] | .[$filled:10] | join("")) as $bar_empty
| "\($cat.name):\n  \($bar_filled)\($bar_empty) \($pct | floor)% (€\($spent | floor)/€\($target)) \($icon)\n"
' | head -100

# Summary
TO_BE_BUDGETED=$(echo "$MONTH_DATA" | jq -r '.data.month.to_be_budgeted / 1000')
AGE_OF_MONEY=$(echo "$MONTH_DATA" | jq -r '.data.month.age_of_money // 0')

echo ""
echo "💰 Da assegnare: €$TO_BE_BUDGETED"
echo "⏱️  Age of Money: $AGE_OF_MONEY giorni"
