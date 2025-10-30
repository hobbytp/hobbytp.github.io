#!/usr/bin/env python3
"""
编码安全包装器
解决Windows系统上的GBK编码问题
"""

import os
import subprocess
import sys

# 设置编码环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

def safe_subprocess_run(*args, **kwargs):
    """安全的subprocess.run包装器"""
    # 确保使用UTF-8编码
    kwargs.setdefault('encoding', 'utf-8')
    kwargs.setdefault('errors', 'replace')
    kwargs.setdefault('text', True)
    
    try:
        return subprocess.run(*args, **kwargs)
    except UnicodeDecodeError as e:
        print(f"编码错误: {e}")
        # 使用更宽松的错误处理
        kwargs['errors'] = 'ignore'
        return subprocess.run(*args, **kwargs)

# 运行目标脚本（默认运行 daily_ai_collector_v2.py，支持自定义目标脚本）
if __name__ == "__main__":
    # 如果提供了参数，则将参数当作目标脚本及其参数
    if len(sys.argv) > 1:
        safe_subprocess_run(["python", *sys.argv[1:]], check=False)
    else:
        # 默认脚本
        safe_subprocess_run(["python", "scripts/daily_ai_collector_v2.py"], check=False)
