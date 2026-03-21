#!/bin/bash
# Generate a code-review-report filename with current timestamp
# Format: code-review-report-<yyyymmddHHMMSS>.json
# Output: Full filename string to stdout

TIMESTAMP=$(date +"%Y%m%d%H%M%S")
echo "code-review-report-${TIMESTAMP}.json"
