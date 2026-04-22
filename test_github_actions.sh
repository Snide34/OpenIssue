#!/bin/bash
# Test script to simulate GitHub Actions workflow locally

set -e

echo "🧪 Testing GitHub Actions workflow locally..."
echo "================================================"

# Step 1: Install CLI (simulating the workflow)
echo "📦 Installing OpenIssue CLI..."
cd cli
pip install -e . > /dev/null 2>&1
echo "✅ CLI installed"

# Step 2: Run security scan (simulating the workflow)
echo "🔍 Running security scan..."
python -m openissue.cli scan .. --sarif results.sarif --json > scan-results.json 2>/dev/null || true

# Step 3: Check if files were created
if [ -f "results.sarif" ]; then
    echo "✅ SARIF file created"
else
    echo "❌ SARIF file missing"
    exit 1
fi

if [ -f "scan-results.json" ]; then
    echo "✅ JSON results created"
else
    echo "❌ JSON results missing"
    exit 1
fi

# Step 4: Parse results (simulating the workflow)
echo "📊 Parsing scan results..."
CRITICAL=$(cat scan-results.json | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('severity_counts', {}).get('CRITICAL', 0))" 2>/dev/null || echo "0")
HIGH=$(cat scan-results.json | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('severity_counts', {}).get('HIGH', 0))" 2>/dev/null || echo "0")
TOTAL=$(cat scan-results.json | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('total', 0))" 2>/dev/null || echo "0")

echo "   Critical: $CRITICAL"
echo "   High: $HIGH"
echo "   Total: $TOTAL"

# Step 5: Validate SARIF format
echo "🔍 Validating SARIF format..."
python -c "
import json
with open('results.sarif', 'r') as f:
    sarif = json.load(f)
    assert sarif.get('version') == '2.1.0'
    assert 'runs' in sarif
    assert len(sarif['runs']) > 0
    assert 'tool' in sarif['runs'][0]
    assert sarif['runs'][0]['tool']['driver']['name'] == 'OpenIssue Security Scanner'
print('✅ SARIF format is valid')
"

# Step 6: Simulate GitHub Actions decision logic
echo "🤖 Simulating GitHub Actions logic..."
if [ "$CRITICAL" -gt "0" ]; then
    echo "❌ CRITICAL vulnerabilities found! Build would fail."
    exit 1
elif [ "$HIGH" -gt "0" ]; then
    echo "⚠️  HIGH vulnerabilities found. Build would continue with warning."
else
    echo "✅ No critical vulnerabilities found. Build would pass."
fi

# Cleanup
rm -f results.sarif scan-results.json

echo "================================================"
echo "🎉 GitHub Actions workflow simulation completed successfully!"
echo "   Your CLI is ready for CI/CD integration."