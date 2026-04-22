# Test script to simulate GitHub Actions workflow locally
# PowerShell version for Windows

Write-Host "🧪 Testing GitHub Actions workflow locally..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

try {
    # Step 1: Install CLI (simulating the workflow)
    Write-Host "📦 Installing OpenIssue CLI..." -ForegroundColor Yellow
    Set-Location cli
    pip install -e . *>$null
    Write-Host "✅ CLI installed" -ForegroundColor Green

    # Step 2: Run security scan (simulating the workflow)
    Write-Host "🔍 Running security scan..." -ForegroundColor Yellow
    python -m openissue.cli scan .. --sarif results.sarif --json > scan-results.json 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Scan completed with warnings (expected)" -ForegroundColor Yellow
    }

    # Step 3: Check if files were created
    if (Test-Path "results.sarif") {
        Write-Host "✅ SARIF file created" -ForegroundColor Green
    } else {
        Write-Host "❌ SARIF file missing" -ForegroundColor Red
        exit 1
    }

    if (Test-Path "scan-results.json") {
        Write-Host "✅ JSON results created" -ForegroundColor Green
    } else {
        Write-Host "❌ JSON results missing" -ForegroundColor Red
        exit 1
    }

    # Step 4: Parse results (simulating the workflow)
    Write-Host "📊 Parsing scan results..." -ForegroundColor Yellow
    
    $jsonContent = Get-Content "scan-results.json" -Raw | ConvertFrom-Json
    $critical = $jsonContent.severity_counts.CRITICAL
    $high = $jsonContent.severity_counts.HIGH
    $total = $jsonContent.total

    Write-Host "   Critical: $critical" -ForegroundColor White
    Write-Host "   High: $high" -ForegroundColor White
    Write-Host "   Total: $total" -ForegroundColor White

    # Step 5: Validate SARIF format
    Write-Host "🔍 Validating SARIF format..." -ForegroundColor Yellow
    $sarifContent = Get-Content "results.sarif" -Raw | ConvertFrom-Json
    
    if ($sarifContent.version -eq "2.1.0" -and 
        $sarifContent.runs -and 
        $sarifContent.runs.Count -gt 0 -and
        $sarifContent.runs[0].tool.driver.name -eq "OpenIssue Security Scanner") {
        Write-Host "✅ SARIF format is valid" -ForegroundColor Green
    } else {
        Write-Host "❌ SARIF format is invalid" -ForegroundColor Red
        exit 1
    }

    # Step 6: Simulate GitHub Actions decision logic
    Write-Host "🤖 Simulating GitHub Actions logic..." -ForegroundColor Yellow
    if ($critical -gt 0) {
        Write-Host "❌ CRITICAL vulnerabilities found! Build would fail." -ForegroundColor Red
        exit 1
    } elseif ($high -gt 0) {
        Write-Host "⚠️  HIGH vulnerabilities found. Build would continue with warning." -ForegroundColor Yellow
    } else {
        Write-Host "✅ No critical vulnerabilities found. Build would pass." -ForegroundColor Green
    }

    # Cleanup
    Remove-Item "results.sarif" -ErrorAction SilentlyContinue
    Remove-Item "scan-results.json" -ErrorAction SilentlyContinue

    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "🎉 GitHub Actions workflow simulation completed successfully!" -ForegroundColor Green
    Write-Host "   Your CLI is ready for CI/CD integration." -ForegroundColor Green

} catch {
    Write-Host "❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Set-Location ..
}