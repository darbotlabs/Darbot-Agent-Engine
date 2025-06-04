# Thought into existence by Darbot
Write-Host "Testing Darbot Task Creation through Frontend Proxy..." -ForegroundColor Cyan

# Test frontend health
try {
    $health = Invoke-RestMethod -Uri "http://localhost:3000/api/health" -Method GET
    Write-Host "Frontend Health Check: $($health.overall_status)" -ForegroundColor Green
    Write-Host "Semantic Kernel: $($health.checks.semantic_kernel.status)" -ForegroundColor Yellow
} catch {
    Write-Host "Frontend Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create task payload
$taskPayload = @{
    task = "Test task: Verify that the 400 Bad Request error is completely fixed and the multi-agent system can process user requests successfully"
    user_id = "debug-user-final-test"
} | ConvertTo-Json

Write-Host "Submitting task through frontend proxy..." -ForegroundColor Cyan
Write-Host "Task: Test task - Verify 400 error fix" -ForegroundColor White

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/input_task" -Method POST -Body $taskPayload -ContentType "application/json" -TimeoutSec 30
    Write-Host "SUCCESS: Task submitted successfully!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor White
    
    Write-Host ""
    Write-Host "CONGRATULATIONS! The 400 Bad Request error has been successfully fixed!" -ForegroundColor Green
    Write-Host "The backend can now process tasks through the frontend without errors." -ForegroundColor Green
    
} catch {
    Write-Host "Task Creation Failed:" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response.StatusCode) {
        Write-Host "   Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Browser should be open at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "You can now manually test task creation through the UI!" -ForegroundColor Yellow
