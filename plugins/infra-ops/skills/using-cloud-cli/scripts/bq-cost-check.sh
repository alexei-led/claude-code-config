#!/bin/bash
# Estimate BigQuery query cost before running
# Usage: bq-cost-check.sh "SELECT * FROM table"

set -euo pipefail

QUERY="$1"
PRICE_PER_TB=5.00

result=$(bq query --dry_run --use_legacy_sql=false --format=json "$QUERY" 2>&1)
bytes=$(echo "$result" | grep -oP 'totalBytesProcessed.*?(\d+)' | grep -oP '\d+' | head -1)

if [ -z "$bytes" ]; then
	echo "Error: Could not estimate query cost"
	echo "$result"
	exit 1
fi

gb=$(echo "scale=2; $bytes / 1024 / 1024 / 1024" | bc)
tb=$(echo "scale=6; $bytes / 1024 / 1024 / 1024 / 1024" | bc)
cost=$(echo "scale=4; $tb * $PRICE_PER_TB" | bc)

echo "Query will scan: ${gb} GB"
echo "Estimated cost: \$${cost}"

if (($(echo "$cost > 1.00" | bc -l))); then
	echo "WARNING: Query cost exceeds $1.00"
	read -p "Continue? (y/N) " -n 1 -r
	echo
	if [[ ! $REPLY =~ ^[Yy]$ ]]; then
		exit 1
	fi
fi
