# 🎮 MACAE Deployment Game - Level 7: Post-Deployment Configuration
# Multi-Agent Custom Automation Engine Configuration Master

Write-Host "🎮 LEVEL 7: POST-DEPLOYMENT CONFIGURATION" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 🎯 Level 7 Objectives
Write-Host "🎯 MISSION OBJECTIVES:" -ForegroundColor Yellow
Write-Host "   • Configure Azure Services" -ForegroundColor White
Write-Host "   • Set Environment Variables" -ForegroundColor White
Write-Host "   • Initialize Agent Framework" -ForegroundColor White
Write-Host "   • Validate Application Health" -ForegroundColor White
Write-Host "   • Setup MCP Connectors" -ForegroundColor White
Write-Host ""

# Variables
$resourceGroup = "Studio-CAT"
$deploymentId = "0ac64f82-105c-4025-9b3d-cf5c4494c52d"

# Achievements tracking
$achievements = @()

Write-Host "🔍 SCANNING DEPLOYED RESOURCES..." -ForegroundColor Cyan

try {
    # Get deployment outputs
    $deployment = az deployment group show --resource-group $resourceGroup --name $deploymentId | ConvertFrom-Json
    
    if ($deployment) {
        Write-Host "✅ ACHIEVEMENT UNLOCKED: Deployment Scout" -ForegroundColor Green
        $achievements += "Deployment Scout"
        
        # Extract key resource names from deployment
        $containerApp = az containerapp list --resource-group $resourceGroup --query "[?contains(name, 'backend')].name" -o tsv
        $frontendApp = az webapp list --resource-group $resourceGroup --query "[?contains(name, 'frontend')].name" -o tsv
        $cosmosAccount = az cosmosdb list --resource-group $resourceGroup --query "[0].name" -o tsv
        $aiServices = az cognitiveservices account list --resource-group $resourceGroup --query "[0].name" -o tsv
        $keyVault = az keyvault list --resource-group $resourceGroup --query "[0].name" -o tsv
        
        Write-Host "🏗️  DISCOVERED RESOURCES:" -ForegroundColor Magenta
        Write-Host "   📦 Backend Container App: $containerApp" -ForegroundColor White
        Write-Host "   🌐 Frontend Web App: $frontendApp" -ForegroundColor White
        Write-Host "   🗄️  Cosmos DB: $cosmosAccount" -ForegroundColor White
        Write-Host "   🧠 AI Services: $aiServices" -ForegroundColor White
        Write-Host "   🔐 Key Vault: $keyVault" -ForegroundColor White
        Write-Host ""
        
        # Sub-mission 1: Configure Cosmos DB
        Write-Host "📊 SUB-MISSION 1: COSMOS DB CONFIGURATION" -ForegroundColor Yellow
        Write-Host "==========================================" -ForegroundColor Yellow
        
        # Check if Cosmos DB database and container exist
        $cosmosDb = az cosmosdb sql database show --account-name $cosmosAccount --resource-group $resourceGroup --name "macae" 2>$null
        if ($cosmosDb) {
            Write-Host "✅ Cosmos DB 'macae' database found" -ForegroundColor Green
            
            $cosmosContainer = az cosmosdb sql container show --account-name $cosmosAccount --resource-group $resourceGroup --database-name "macae" --name "memory" 2>$null
            if ($cosmosContainer) {
                Write-Host "✅ Cosmos DB 'memory' container found" -ForegroundColor Green
                Write-Host "✅ ACHIEVEMENT UNLOCKED: Database Architect" -ForegroundColor Green
                $achievements += "Database Architect"
            } else {
                Write-Host "⚠️  Memory container not found - this should have been created by deployment" -ForegroundColor Yellow
            }
        } else {
            Write-Host "⚠️  Cosmos database not found - this should have been created by deployment" -ForegroundColor Yellow
        }
        
        # Sub-mission 2: Validate AI Services Deployment
        Write-Host ""
        Write-Host "🧠 SUB-MISSION 2: AI SERVICES VALIDATION" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Yellow
        
        $gptDeployment = az cognitiveservices account deployment show --name $aiServices --resource-group $resourceGroup --deployment-name "gpt-4o" 2>$null
        if ($gptDeployment) {
            $deploymentInfo = $gptDeployment | ConvertFrom-Json
            Write-Host "✅ GPT-4o model deployed successfully" -ForegroundColor Green
            Write-Host "   📊 Capacity: $($deploymentInfo.sku.capacity)" -ForegroundColor White
            Write-Host "   🎯 Status: $($deploymentInfo.properties.provisioningState)" -ForegroundColor White
            Write-Host "✅ ACHIEVEMENT UNLOCKED: AI Whisperer" -ForegroundColor Green
            $achievements += "AI Whisperer"
        } else {
            Write-Host "❌ GPT-4o deployment not found" -ForegroundColor Red
        }
        
        # Sub-mission 3: Container App Health Check
        Write-Host ""
        Write-Host "📦 SUB-MISSION 3: CONTAINER APP HEALTH CHECK" -ForegroundColor Yellow
        Write-Host "=============================================" -ForegroundColor Yellow
        
        if ($containerApp) {
            $appStatus = az containerapp show --name $containerApp --resource-group $resourceGroup --query "properties.provisioningState" -o tsv
            $appUrl = az containerapp show --name $containerApp --resource-group $resourceGroup --query "properties.configuration.ingress.fqdn" -o tsv
            
            Write-Host "📦 Backend Container App Status: $appStatus" -ForegroundColor White
            if ($appUrl) {
                Write-Host "🌐 Backend URL: https://$appUrl" -ForegroundColor White
                Write-Host "✅ ACHIEVEMENT UNLOCKED: Container Captain" -ForegroundColor Green
                $achievements += "Container Captain"
            }
        }
        
        # Sub-mission 4: Frontend Web App Check
        Write-Host ""
        Write-Host "🌐 SUB-MISSION 4: FRONTEND WEB APP CHECK" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Yellow
        
        if ($frontendApp) {
            $frontendStatus = az webapp show --name $frontendApp --resource-group $resourceGroup --query "state" -o tsv
            $frontendUrl = az webapp show --name $frontendApp --resource-group $resourceGroup --query "defaultHostName" -o tsv
            
            Write-Host "🌐 Frontend Status: $frontendStatus" -ForegroundColor White
            if ($frontendUrl) {
                Write-Host "🌐 Frontend URL: https://$frontendUrl" -ForegroundColor White
                Write-Host "✅ ACHIEVEMENT UNLOCKED: Frontend Master" -ForegroundColor Green
                $achievements += "Frontend Master"
            }
        }
        
        # Sub-mission 5: Environment Variables Configuration
        Write-Host ""
        Write-Host "⚙️  SUB-MISSION 5: ENVIRONMENT VARIABLES CHECK" -ForegroundColor Yellow
        Write-Host "==============================================" -ForegroundColor Yellow
        
        # Get environment variables from container app
        $envVars = az containerapp show --name $containerApp --resource-group $resourceGroup --query "properties.template.containers[0].env" -o json | ConvertFrom-Json
        
        $requiredEnvVars = @(
            "COSMOSDB_ENDPOINT",
            "COSMOSDB_DATABASE", 
            "COSMOSDB_CONTAINER",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "AZURE_AI_AGENT_PROJECT_CONNECTION_STRING",
            "AZURE_AI_SUBSCRIPTION_ID",
            "AZURE_AI_RESOURCE_GROUP",
            "AZURE_AI_PROJECT_NAME"
        )
        
        $missingVars = @()
        foreach ($reqVar in $requiredEnvVars) {
            $found = $envVars | Where-Object { $_.name -eq $reqVar }            if ($found) {
                Write-Host "✅ ${reqVar}: configured" -ForegroundColor Green
            } else {
                Write-Host "❌ ${reqVar}: missing" -ForegroundColor Red
                $missingVars += $reqVar
            }
        }
        
        if ($missingVars.Count -eq 0) {
            Write-Host "✅ ACHIEVEMENT UNLOCKED: Configuration Wizard" -ForegroundColor Green
            $achievements += "Configuration Wizard"
        } else {
            Write-Host "⚠️  Missing environment variables detected" -ForegroundColor Yellow
        }
        
        # Sub-mission 6: API Health Check
        Write-Host ""
        Write-Host "🔍 SUB-MISSION 6: API HEALTH CHECK" -ForegroundColor Yellow
        Write-Host "===================================" -ForegroundColor Yellow
        
        if ($appUrl) {
            try {
                $healthCheck = Invoke-RestMethod -Uri "https://$appUrl/health" -Method Get -TimeoutSec 10 -ErrorAction SilentlyContinue
                if ($healthCheck) {
                    Write-Host "✅ Backend API is responding" -ForegroundColor Green
                    Write-Host "✅ ACHIEVEMENT UNLOCKED: API Guardian" -ForegroundColor Green
                    $achievements += "API Guardian"
                } else {
                    Write-Host "⚠️  API health check inconclusive" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "⚠️  API health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
                Write-Host "   This is normal if the application is still starting up" -ForegroundColor Gray
            }
        }
        
        # LEVEL 7 COMPLETION SUMMARY
        Write-Host ""
        Write-Host "🏆 LEVEL 7 COMPLETION SUMMARY" -ForegroundColor Cyan
        Write-Host "=============================" -ForegroundColor Cyan
        Write-Host "📊 Achievements Earned: $($achievements.Count)" -ForegroundColor Yellow
        foreach ($achievement in $achievements) {
            Write-Host "   🏅 $achievement" -ForegroundColor Green
        }
        
        $completionRate = [math]::Round(($achievements.Count / 6) * 100, 0)
        Write-Host ""
        Write-Host "📈 Level 7 Completion: $completionRate%" -ForegroundColor Yellow
        
        if ($completionRate -ge 80) {
            Write-Host "🎉 EXCELLENT! Ready for Level 8: Agent Framework Activation" -ForegroundColor Green
        } elseif ($completionRate -ge 60) {
            Write-Host "👍 GOOD! Minor issues detected, but deployable" -ForegroundColor Yellow
        } else {
            Write-Host "⚠️  NEEDS ATTENTION: Several configuration issues detected" -ForegroundColor Red
        }
        
        # Next Steps
        Write-Host ""
        Write-Host "🎯 NEXT LEVEL PREVIEW: AGENT FRAMEWORK ACTIVATION" -ForegroundColor Magenta
        Write-Host "• Initialize multi-agent orchestration system" -ForegroundColor White
        Write-Host "• Configure agent workflows and capabilities" -ForegroundColor White  
        Write-Host "• Setup MCP (Model Context Protocol) connectors" -ForegroundColor White
        Write-Host "• Test agent-to-agent communication" -ForegroundColor White
        Write-Host "• Validate Darbotian philosophy implementation" -ForegroundColor White
        Write-Host ""
        
    } else {
        Write-Host "❌ LEVEL 7 FAILED: Deployment not found" -ForegroundColor Red
        Write-Host "   Please complete Level 6 (deployment) first" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ LEVEL 7 ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Debug info saved to logs/level7-error.log" -ForegroundColor Yellow
    
    # Save error log
    $errorLog = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Level = "Level 7"
        Error = $_.Exception.Message
        StackTrace = $_.Exception.StackTrace
    }
    $errorLog | ConvertTo-Json | Out-File -FilePath "logs/level7-error.log" -Append
}

Write-Host ""
Write-Host "🎮 Level 7 Complete! Ready to activate the agent framework?" -ForegroundColor Cyan
Write-Host "   Run .\scripts\validate-agent-framework.ps1 to continue" -ForegroundColor White
Write-Host ""
