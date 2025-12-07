#!/usr/bin/env python3
"""
修复 Cloudflare API Token 格式问题
检查并清理 .env 文件中的 token
"""

import os
import re
from pathlib import Path

def clean_token(token: str) -> str:
    """清理 token：移除引号、空白字符、换行符"""
    if not token:
        return token
    
    # 移除前后空白字符
    token = token.strip()
    
    # 移除引号包裹
    if (token.startswith('"') and token.endswith('"')) or \
       (token.startswith("'") and token.endswith("'")):
        token = token[1:-1].strip()
    
    # 移除所有空白字符和换行符
    token = ''.join(token.split())
    
    return token

def check_token_format(token: str) -> dict:
    """检查 token 格式"""
    issues = []
    warnings = []
    
    if not token:
        issues.append("Token 为空")
        return {"valid": False, "issues": issues, "warnings": warnings}
    
    # 检查长度
    if len(token) < 30:
        warnings.append(f"Token 长度异常短（{len(token)} 字符），Cloudflare API Token 通常是 40-50 个字符")
    elif len(token) > 60:
        warnings.append(f"Token 长度异常长（{len(token)} 字符）")
    
    # 检查字符
    invalid_chars = [c for c in token if not re.match(r'[A-Za-z0-9_-]', c)]
    if invalid_chars:
        issues.append(f"包含无效字符: {set(invalid_chars)}")
        issues.append(f"无效字符的 ASCII 码: {[ord(c) for c in list(set(invalid_chars))[:5]]}")
    
    # 检查空白字符
    if ' ' in token or '\n' in token or '\r' in token or '\t' in token:
        issues.append("包含空白字符（空格、换行符或制表符）")
    
    # 检查引号
    if '"' in token or "'" in token:
        issues.append("包含引号字符")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "length": len(token)
    }

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 Cloudflare API Token 格式修复工具")
    print("=" * 60)
    
    env_file = Path('.env')
    if not env_file.exists():
        print(f"\n❌ 未找到 .env 文件: {env_file.absolute()}")
        return
    
    print(f"\n📄 读取 .env 文件: {env_file.absolute()}")
    
    # 读取 .env 文件
    lines = []
    token_line_index = -1
    token_line = None
    
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 查找 CLOUDFLARE_API_TOKEN 行
    for i, line in enumerate(lines):
        if line.strip().startswith('CLOUDFLARE_API_TOKEN='):
            token_line_index = i
            token_line = line
            break
    
    if token_line_index == -1:
        print("\n❌ 未找到 CLOUDFLARE_API_TOKEN 行")
        return
    
    print(f"\n找到 Token 行 (第 {token_line_index + 1} 行):")
    print(f"  原始内容: {repr(token_line)}")
    
    # 提取 token 值
    if '=' in token_line:
        _, token_value = token_line.split('=', 1)
        original_token = token_value.strip()
        cleaned_token = clean_token(original_token)
        
        print(f"\n📊 Token 分析:")
        print(f"  原始 Token 长度: {len(original_token)}")
        print(f"  清理后 Token 长度: {len(cleaned_token)}")
        print(f"  原始 Token 预览: {repr(original_token[:20])}...")
        print(f"  清理后 Token 预览: {repr(cleaned_token[:20])}...")
        
        # 检查格式
        check_result = check_token_format(cleaned_token)
        
        print(f"\n🔍 格式检查结果:")
        if check_result["valid"]:
            print(f"  ✅ Token 格式有效")
        else:
            print(f"  ❌ Token 格式有问题:")
            for issue in check_result["issues"]:
                print(f"     - {issue}")
        
        if check_result["warnings"]:
            print(f"\n  ⚠️  警告:")
            for warning in check_result["warnings"]:
                print(f"     - {warning}")
        
        # 如果 token 需要清理，提供修复建议
        if original_token != cleaned_token or not check_result["valid"]:
            print(f"\n💡 修复建议:")
            print(f"  1. 将 .env 文件中的 CLOUDFLARE_API_TOKEN 行修改为:")
            print(f"     CLOUDFLARE_API_TOKEN={cleaned_token}")
            print(f"\n  2. 或者手动编辑 .env 文件，确保:")
            print(f"     - 没有引号包裹 token")
            print(f"     - 没有空白字符")
            print(f"     - 没有换行符")
            print(f"     - Token 只包含字母、数字、下划线和连字符")
            
            # 询问是否自动修复
            print(f"\n❓ 是否自动修复 .env 文件？(y/n): ", end='')
            try:
                answer = input().strip().lower()
                if answer == 'y':
                    # 修复文件
                    lines[token_line_index] = f"CLOUDFLARE_API_TOKEN={cleaned_token}\n"
                    with open(env_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print(f"\n✅ 已自动修复 .env 文件")
                    print(f"   新内容: CLOUDFLARE_API_TOKEN={cleaned_token[:20]}...")
                else:
                    print(f"\n⏭️  跳过自动修复，请手动修复 .env 文件")
            except KeyboardInterrupt:
                print(f"\n\n⏭️  已取消")
        else:
            print(f"\n✅ Token 格式正确，无需修复")
    else:
        print(f"\n❌ 无法解析 Token 行格式")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()





