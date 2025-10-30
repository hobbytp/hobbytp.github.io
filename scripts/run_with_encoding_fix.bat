@echo off
REM 设置编码环境变量并运行脚本
set PYTHONUTF8=1
set PYTHONIOENCODING=UTF-8

echo 环境变量设置:
echo PYTHONUTF8=%PYTHONUTF8%
echo PYTHONIOENCODING=%PYTHONIOENCODING%
echo.

echo 运行每日AI收集器...
python scripts/daily_ai_collector_v2.py

pause


