$payload = @{session_id = "test123"; description = "Create a simple onboarding checklist"} | ConvertTo-Json 
Invoke-RestMethod -Uri "http://localhost:8001/api/input_task" -Method Post -ContentType "application/json" -Body $payload
