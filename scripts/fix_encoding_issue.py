#!/usr/bin/env python3
"""
修复Windows系统上的编码问题
解决UnicodeDecodeError: 'gbk' codec can't decode byte问题
"""

import os
import subprocess
import locale

def fix_encoding_issues():
    """修复编码问题"""
    print("=" * 60)
    print("修复Windows编码问题")
    print("=" * 60)
    
    # 1. 设置环境变量
    print("1. 设置环境变量...")
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # 2. 检查当前编码设置
    print(f"当前系统编码: {locale.getpreferredencoding()}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', '未设置')}")
    print(f"PYTHONUTF8: {os.environ.get('PYTHONUTF8', '未设置')}")
    
    # 3. 创建一个安全的subprocess包装器
    def safe_subprocess_run(*args, **kwargs):
        """安全的subprocess.run包装器"""
        # 确保使用UTF-8编码
        kwargs.setdefault('encoding', 'utf-8')
        kwargs.setdefault('errors', 'replace')  # 遇到无法解码的字符时替换
        kwargs.setdefault('text', True)
        
        try:
            return subprocess.run(*args, **kwargs)
        except UnicodeDecodeError as e:
            print(f"编码错误: {e}")
            # 使用更宽松的错误处理
            kwargs['errors'] = 'ignore'
            return subprocess.run(*args, **kwargs)
    
    return safe_subprocess_run

def test_encoding_fix(run_func):
    """测试编码修复"""
    print("\n2. 测试编码修复...")
    
    # 测试中文字符输出
    test_strings = [
        "测试中文字符",
        "AI技术动态",
        "每日AI动态收集器",
        "编码问题修复"
    ]
    
    for test_str in test_strings:
        try:
            print(f"测试字符串: {test_str}")
            # 使用安全的子进程运行函数
            result = run_func(
                ['python', '-c', f'print("{test_str}")'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            print(f"输出: {result.stdout.strip()}")
        except Exception as e:
            print(f"错误: {e}")

def create_encoding_safe_script():
    """创建编码安全的脚本包装器"""
    print("\n3. 创建编码安全包装器...")
    
    wrapper_content = '''#!/usr/bin/env python3
"""
编码安全包装器
解决Windows系统上的GBK编码问题
"""

import os
import sys
import subprocess

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
    if len(sys.argv) > 1:
        safe_subprocess_run(["python", *sys.argv[1:]], check=False)
    else:
        safe_subprocess_run(["python", "scripts/daily_ai_collector_v2.py"], check=False)
'''
    
    with open('scripts/encoding_safe_runner.py', 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    print("已创建 scripts/encoding_safe_runner.py")

def main():
    """主函数"""
    print("开始修复编码问题...")
    
    # 1. 修复编码问题
    safe_run = fix_encoding_issues()
    
    # 2. 测试修复
    test_encoding_fix(safe_run)
    
    # 3. 创建安全包装器
    create_encoding_safe_script()
    
    print("\n" + "=" * 60)
    print("编码问题修复完成！")
    print("=" * 60)
    print("\n使用方法:")
    print("1. 直接运行: python scripts/encoding_safe_runner.py")
    print("2. 或者设置环境变量后运行原脚本:")
    print("   set PYTHONIOENCODING=utf-8")
    print("   python scripts/daily_ai_collector_v2.py")

if __name__ == "__main__":
    main()


