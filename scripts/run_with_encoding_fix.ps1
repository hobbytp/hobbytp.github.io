# PowerShell脚本：设置编码环境变量并运行脚本

# 设置环境变量
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "UTF-8"

Write-Host "环境变量设置:" -ForegroundColor Green
Write-Host "PYTHONUTF8=$env:PYTHONUTF8"
Write-Host "PYTHONIOENCODING=$env:PYTHONIOENCODING"
Write-Host ""

Write-Host "运行每日AI收集器..." -ForegroundColor Yellow
python scripts/daily_ai_collector_v2.py

Write-Host "按任意键继续..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")



