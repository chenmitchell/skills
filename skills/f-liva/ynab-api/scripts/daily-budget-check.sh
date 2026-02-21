#!/bin/bash
# Daily budget check - comprehensive morning report
# Designed to be called by cron job

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

YNAB_API="https://api.ynab.com/v1"
TODAY=$(date -u '+%Y-%m-%d')
TOMORROW=$(date -u -d "+1 day" '+%Y-%m-%d')
END_7_DAYS=$(date -u -d "+7 days" '+%Y-%m-%d')

# Get current month data
MONTH_DATA=$(curl -s "$YNAB_API/budgets/$BUDGET_ID/months/current" \
  -H "Authorization: Bearer $API_KEY")

# Get scheduled transactions
SCHEDULED=$(curl -s "$YNAB_API/budgets/$BUDGET_ID/scheduled_transactions" \
  -H "Authorization: Bearer $API_KEY")

# Build report
echo "*☀️ BUDGET CHECK MATTUTINO*"
echo ""

# Age of Money
AGE_OF_MONEY=$(echo "$MONTH_DATA" | jq -r '.data.month.age_of_money // 0')
if [ "$AGE_OF_MONEY" -ge 120 ]; then
  AOM_ICON="✅"
elif [ "$AGE_OF_MONEY" -ge 60 ]; then
  AOM_ICON="🟡"
else
  AOM_ICON="⚠️"
fi
echo "*💰 Age of Money: $AGE_OF_MONEY giorni* $AOM_ICON"
echo ""

# Upcoming scheduled transactions (next 7 days)
UPCOMING_COUNT=$(echo "$SCHEDULED" | jq --arg today "$TODAY" --arg end "$END_7_DAYS" '
[.data.scheduled_transactions[]
| select(.date_next >= $today and .date_next <= $end and .deleted == false)]
| length
')

if [ "$UPCOMING_COUNT" -gt 0 ]; then
  echo "*📅 Prossime uscite (7gg)*"
  echo "$SCHEDULED" | jq -r --arg today "$TODAY" --arg end "$END_7_DAYS" '
  .data.scheduled_transactions[]
  | select(.date_next >= $today and .date_next <= $end and .deleted == false and .amount < 0)
  | . as $tx
  | ($tx.amount / -1000) as $amount
  | if $tx.date_next == $today then "• Oggi: " elif $tx.date_next == ($today | split("-") | .[0:2] | join("-") + "-" + (.[2] | tonumber + 1 | tostring)) then "• Domani: " else "• \($tx.date_next): " end + "\($tx.payee_name) €\($amount)"
  ' | head -5
  echo ""
fi

# Overspending alerts
OVERSPENT=$(echo "$MONTH_DATA" | jq -r '
.data.month.categories[]
| select(.goal_type != null and .deleted == false)
| . as $cat
| ($cat.activity / -1000) as $spent
| ($cat.goal_target / 1000) as $target
| if $target > 0 and $spent > $target then
    "\($cat.name): €\($spent | floor) / €\($target) (+€\(($spent - $target) | floor))"
  else empty end
' | head -3)

if [ -n "$OVERSPENT" ]; then
  echo "*⚠️ Alert Budget Superato*"
  echo "$OVERSPENT" | while IFS= read -r line; do
    echo "• $line"
  done
  echo ""
fi

# Goals needing attention (< 20% complete and significant target)
GOALS_LOW=$(echo "$MONTH_DATA" | jq -r '
.data.month.categories[]
| select(.goal_type != null and .deleted == false)
| . as $cat
| ($cat.activity / -1000) as $spent
| ($cat.goal_target / 1000) as $target
| if $target >= 100 then
    ($spent / $target * 100) as $pct
    | if $pct < 20 then
        "\($cat.name): \($pct | floor)% (€\($spent | floor)/€\($target))"
      else empty end
  else empty end
' | head -3)

if [ -n "$GOALS_LOW" ]; then
  echo "*🎯 Obiettivi in ritardo*"
  echo "$GOALS_LOW" | while IFS= read -r line; do
    echo "• $line"
  done
  echo ""
fi

# To be budgeted
TO_BE_BUDGETED=$(echo "$MONTH_DATA" | jq -r '.data.month.to_be_budgeted / 1000')
if (( $(echo "$TO_BE_BUDGETED > 0" | bc -l) )); then
  echo "*💵 Da assegnare: €$TO_BE_BUDGETED*"
fi
