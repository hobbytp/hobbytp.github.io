#!/usr/bin/env python3
"""
测试 Cloudflare API 认证和连接
用于诊断 401 认证错误
"""

import os
import sys
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def test_env_vars():
    """测试环境变量是否加载"""
    print("=" * 60)
    print("🔍 环境变量检查")
    print("=" * 60)
    
    account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    index_name = os.getenv('CLOUDFLARE_VECTORIZE_INDEX_NAME', 'blog-index')
    
    # 检查 .env 文件
    env_file = Path('.env')
    if env_file.exists():
        print(f"✅ 找到 .env 文件: {env_file.absolute()}")
    else:
        print(f"⚠️  未找到 .env 文件")
    
    print(f"\n环境变量状态:")
    if account_id:
        print(f"  ✅ CLOUDFLARE_ACCOUNT_ID: {account_id[:8]}...{account_id[-4:] if len(account_id) > 12 else ''} (长度: {len(account_id)})")
    else:
        print(f"  ❌ CLOUDFLARE_ACCOUNT_ID: 未设置")
    
    if api_token:
        # 清理token：移除引号、空白字符、换行符
        original_token = api_token
        api_token = api_token.strip()
        # 移除可能的引号包裹
        if (api_token.startswith('"') and api_token.endswith('"')) or \
           (api_token.startswith("'") and api_token.endswith("'")):
            api_token = api_token[1:-1].strip()
            print(f"  ⚠️  警告: API Token 被引号包裹，已自动移除")
        
        # 移除所有空白字符和换行符
        api_token_clean = ''.join(api_token.split())
        if api_token != api_token_clean:
            print(f"  ⚠️  警告: API Token 包含空白字符或换行符，已清理")
            api_token = api_token_clean
        
        # 检查token格式
        token_preview = f"{api_token[:8]}...{api_token[-4:]}" if len(api_token) > 12 else "***"
        print(f"  ✅ CLOUDFLARE_API_TOKEN: {token_preview} (长度: {len(api_token)})")
        
        # 检查token格式（Cloudflare API Token通常是40-50个字符，base64编码）
        if len(api_token) < 40:
            print(f"  ⚠️  警告: API Token 长度异常短（{len(api_token)}字符），Cloudflare API Token 通常是 40-50 个字符")
            print(f"      可能的原因：")
            print(f"      1. Token 不完整（复制时可能被截断）")
            print(f"      2. Token 格式不正确")
            print(f"      3. 使用了错误的 token 类型")
            print(f"      建议：重新生成 API Token 并确保完整复制")
        elif len(api_token) > 60:
            print(f"  ⚠️  警告: API Token 长度异常长（{len(api_token)}字符），可能包含额外字符")
        
        # 检查是否包含非base64字符（Cloudflare token通常是base64编码）
        import re
        if not re.match(r'^[A-Za-z0-9_-]+$', api_token):
            print(f"  ⚠️  警告: API Token 包含特殊字符，可能格式不正确")
            print(f"      Token 应只包含字母、数字、下划线和连字符")
    else:
        print(f"  ❌ CLOUDFLARE_API_TOKEN: 未设置")
    
    print(f"  📦 CLOUDFLARE_VECTORIZE_INDEX_NAME: {index_name}")
    
    # 检查代理设置
    http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
    https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
    if http_proxy or https_proxy:
        print(f"\n🌐 代理设置:")
        if http_proxy:
            print(f"  HTTP_PROXY: {http_proxy}")
        if https_proxy:
            print(f"  HTTPS_PROXY: {https_proxy}")
    
    # 清理并返回token
    if api_token:
        api_token_clean = api_token.strip()
        # 移除引号
        if (api_token_clean.startswith('"') and api_token_clean.endswith('"')) or \
           (api_token_clean.startswith("'") and api_token_clean.endswith("'")):
            api_token_clean = api_token_clean[1:-1].strip()
        # 移除所有空白字符
        api_token_clean = ''.join(api_token_clean.split())
        return account_id, api_token_clean, index_name
    
    return account_id, api_token, index_name

def test_api_connection(account_id: str, api_token: str):
    """测试 API 连接"""
    if not account_id or not api_token:
        print("\n❌ 无法测试 API 连接：缺少必要的环境变量")
        return False
    
    print("\n" + "=" * 60)
    print("🔗 API 连接测试")
    print("=" * 60)
    
    import requests
    
    # 测试1: 验证账户ID和Token
    print("\n1️⃣ 测试账户验证...")
    print(f"   使用 Token (长度: {len(api_token)})")
    
    # 详细检查 token 内容
    print(f"\n   🔍 Token 详细检查:")
    print(f"      - 原始长度: {len(api_token)}")
    print(f"      - 是否包含空白字符: {any(c.isspace() for c in api_token)}")
    print(f"      - 是否包含不可打印字符: {any(not c.isprintable() and not c.isspace() for c in api_token)}")
    print(f"      - 字符编码检查: {api_token.encode('utf-8', errors='strict')[:20]}...")
    
    # 显示 token 的十六进制表示（前20字节）
    token_bytes = api_token.encode('utf-8')
    hex_preview = ' '.join(f'{b:02x}' for b in token_bytes[:20])
    print(f"      - 十六进制预览: {hex_preview}...")
    
    # 检查 token 格式（Cloudflare API Token 通常是 base64 编码）
    import base64
    import re
    is_base64_like = bool(re.match(r'^[A-Za-z0-9_-]+$', api_token))
    print(f"      - 是否符合 base64 格式: {is_base64_like}")
    
    if not is_base64_like:
        print(f"      ⚠️  警告: Token 包含非 base64 字符")
        invalid_chars = [c for c in api_token if not re.match(r'[A-Za-z0-9_-]', c)]
        if invalid_chars:
            print(f"      - 无效字符: {set(invalid_chars)}")
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}"
    auth_header = f"Bearer {api_token}"
    print(f"\n   📤 Authorization Header 预览:")
    print(f"      - 格式: Bearer <token>")
    print(f"      - Header 长度: {len(auth_header)}")
    print(f"      - Header 前30字符: {auth_header[:30]}...")
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    # 配置代理
    proxies = None
    http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
    https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
    if http_proxy or https_proxy:
        proxies = {
            'http': http_proxy,
            'https': https_proxy or http_proxy
        }
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                account_name = result.get('result', {}).get('name', 'Unknown')
                print(f"   ✅ 账户验证成功: {account_name}")
            else:
                print(f"   ❌ 账户验证失败: {result}")
                return False
        elif response.status_code == 400:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('errors', [{}])[0].get('message', 'Unknown error')
            error_chain = error_data.get('errors', [{}])[0].get('error_chain', [])
            print(f"   ❌ 请求失败 (400): {error_msg}")
            if error_chain:
                chain_msg = error_chain[0].get('message', '')
                print(f"      详细错误: {chain_msg}")
            
            # 如果是 Authorization header 格式错误，提供更详细的诊断
            if 'Authorization header' in error_msg or any('Authorization header' in str(e) for e in error_chain):
                print(f"\n   🔍 Authorization Header 诊断:")
                print(f"      - 当前格式: 'Bearer {api_token[:10]}...'")
                print(f"      - Token 长度: {len(api_token)}")
                
                # 检查 token 长度
                if len(api_token) < 40:
                    print(f"      ⚠️  严重警告: Token 长度异常短（{len(api_token)}字符）")
                    print(f"         Cloudflare API Token 通常是 40-50 个字符")
                    print(f"         可能的原因：")
                    print(f"         1. Token 不完整（复制时被截断）")
                    print(f"         2. 使用了错误的 token 类型")
                    print(f"         3. Token 格式不正确")
                
                print(f"      - Token 是否为空: {not api_token}")
                print(f"      - Token 是否包含空格: {' ' in api_token}")
                newline = '\n'
                carriage_return = '\r'
                print(f"      - Token 是否包含换行符: {newline in api_token or carriage_return in api_token}")
                
                # 检查 token 字符
                invalid_chars = [c for c in api_token if not c.isalnum() and c not in '_-']
                if invalid_chars:
                    print(f"      - 包含特殊字符: {set(invalid_chars)}")
                
                print(f"\n   💡 修复建议:")
                if len(api_token) < 40:
                    print(f"      ⚠️  优先处理: Token 长度异常，请重新生成 API Token")
                    print(f"         1. 访问 https://dash.cloudflare.com/profile/api-tokens")
                    print(f"         2. 创建新 Token（确保有 Workers AI 和 Vectorize 权限）")
                    print(f"         3. 完整复制 Token（应该是 40-50 个字符）")
                    print(f"         4. 更新 .env 文件中的 CLOUDFLARE_API_TOKEN")
                print(f"      1. 检查 .env 文件，确保 CLOUDFLARE_API_TOKEN 是纯字符串")
                print(f"      2. 移除所有引号、空白字符、换行符")
                print(f"      3. Token 应该只包含字母、数字、下划线和连字符")
                print(f"      4. 如果问题持续，查看详细排查指南: docs/cloudflare-auth-troubleshooting.md")
            
            return False
        elif response.status_code == 401:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('errors', [{}])[0].get('message', 'Unknown error')
            print(f"   ❌ 认证失败 (401): {error_msg}")
            print(f"\n   可能的原因:")
            print(f"   1. API Token 无效或已过期")
            print(f"   2. API Token 格式错误（可能包含换行符或多余字符）")
            print(f"   3. 环境变量未正确加载")
            print(f"\n   解决方案:")
            print(f"   1. 检查 .env 文件中的 CLOUDFLARE_API_TOKEN 是否正确")
            print(f"   2. 确保 .env 文件中没有引号包裹 token（除非token本身包含引号）")
            print(f"   3. 重新生成 API Token: https://dash.cloudflare.com/profile/api-tokens")
            return False
        elif response.status_code == 403:
            print(f"   ❌ 权限不足 (403)")
            print(f"   请确保 API Token 有 Account:Read 权限")
            return False
        else:
            print(f"   ❌ 请求失败: HTTP {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
            
    except requests.exceptions.ProxyError as e:
        print(f"   ❌ 代理连接失败: {e}")
        print(f"   请检查代理设置或临时禁用代理环境变量")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ 网络连接失败: {e}")
        print(f"   请检查网络连接")
        return False
    except Exception as e:
        print(f"   ❌ 发生错误: {e}")
        return False
    
    # 测试2: 测试 Workers AI 访问（使用实际的 AI run 端点）
    print("\n2️⃣ 测试 Workers AI 访问...")
    # 使用一个简单的 embedding 模型测试
    ai_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/baai/bge-base-en-v1.5"
    try:
        # 使用 POST 请求测试 embedding 模型
        test_response = requests.post(
            ai_url,
            headers=headers,
            json={"text": "test"},
            proxies=proxies,
            timeout=10
        )
        if test_response.status_code == 200:
            print(f"   ✅ Workers AI 可访问（Embedding 模型测试成功）")
        elif test_response.status_code == 401:
            print(f"   ❌ Workers AI 认证失败 (401)")
            print(f"   请确保 API Token 有 Workers AI 权限")
            return False
        elif test_response.status_code == 403:
            print(f"   ❌ Workers AI 权限不足 (403)")
            print(f"   请确保 API Token 有 Account: Cloudflare Workers AI:Edit 权限")
            return False
        else:
            # 如果 POST 失败，尝试检查账户是否有 Workers AI 访问权限
            print(f"   ⚠️  Workers AI 测试返回: HTTP {test_response.status_code}")
            if test_response.status_code == 400:
                error_data = test_response.json() if test_response.content else {}
                print(f"      响应: {error_data}")
                print(f"      注意: 这可能是正常的（模型参数问题），但说明 API 可访问")
    except Exception as e:
        print(f"   ⚠️  Workers AI 测试失败: {e}")
    
    # 测试3: 测试 Vectorize 访问
    print("\n3️⃣ 测试 Vectorize 访问...")
    vectorize_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/vectorize/indexes"
    try:
        response = requests.get(vectorize_url, headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            result = response.json()
            # 处理不同的响应格式
            if isinstance(result.get('result'), dict):
                indexes = result.get('result', {}).get('indexes', [])
            elif isinstance(result.get('result'), list):
                indexes = result.get('result', [])
            else:
                indexes = []
            
            print(f"   ✅ Vectorize 可访问，找到 {len(indexes)} 个索引")
            if indexes:
                print(f"   索引列表:")
                for idx in indexes[:5]:  # 只显示前5个
                    if isinstance(idx, dict):
                        print(f"     - {idx.get('name', 'Unknown')}")
                    else:
                        print(f"     - {idx}")
        elif response.status_code == 401:
            print(f"   ❌ Vectorize 认证失败 (401)")
            print(f"   请确保 API Token 有 Vectorize 权限")
            return False
        elif response.status_code == 403:
            print(f"   ❌ Vectorize 权限不足 (403)")
            print(f"   请确保 API Token 有 Account: Vectorize:Edit 权限")
            return False
        else:
            print(f"   ⚠️  Vectorize 访问异常: HTTP {response.status_code}")
            if response.content:
                try:
                    error_data = response.json()
                    print(f"      响应: {error_data}")
                except:
                    print(f"      响应: {response.text[:200]}")
    except Exception as e:
        print(f"   ⚠️  Vectorize 测试失败: {e}")
        import traceback
        print(f"      详细错误: {traceback.format_exc()}")
    
    return True

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🧪 Cloudflare API 认证测试工具")
    print("=" * 60)
    
    account_id, api_token, index_name = test_env_vars()
    
    if not account_id or not api_token:
        print("\n❌ 缺少必要的环境变量，无法继续测试")
        print("\n请设置以下环境变量:")
        print("  - CLOUDFLARE_ACCOUNT_ID")
        print("  - CLOUDFLARE_API_TOKEN")
        print("\n可以在 .env 文件中设置，或通过环境变量设置")
        sys.exit(1)
    
    success = test_api_connection(account_id, api_token)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！可以运行 scripts/ingest.py")
    else:
        print("❌ 测试失败，请根据上述错误信息修复问题")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

