#!/usr/bin/env python3
"""
测试改进后的AI封面生成功能
验证横屏尺寸和无文字/人物的生成效果
"""

import os
import sys
from pathlib import Path

# 添加scripts目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from ai_cover_generator import CoverImageGenerator, ImageGenConfig

def test_cover_generation():
    """测试封面生成"""
    print("🎨 测试改进后的AI封面生成功能")
    print("=" * 50)

    # 检查环境变量
    modelscope_key = os.getenv("MODELSCOPE_API_KEY")
    if not modelscope_key:
        print("❌ 未设置 MODELSCOPE_API_KEY 环境变量")
        print("请在 .env 文件中添加: MODELSCOPE_API_KEY=your-key")
        return False

    # 创建配置
    config = ImageGenConfig(
        api_provider="modelscope",
        api_key=modelscope_key,
        width=1200,  # 横屏宽度
        height=630,   # 横屏高度 (16:9比例)
        style_suffix="abstract geometric pattern, professional blog cover, clean design, minimal, technology theme, no text, no letters, no words, no people, no faces, no portraits, landscape orientation, widescreen format"
    )

    print(f"✅ 配置信息:")
    print(f"   - API提供商: {config.api_provider}")
    print(f"   - 模型: {config.model}")
    print(f"   - 图片尺寸: {config.width}x{config.height}")
    print(f"   - 样式: {config.style_suffix}")
    print()

    # 创建生成器
    generator = CoverImageGenerator(config)

    # 测试用例
    test_cases = [
        {
            "title": "深度学习与神经网络最新进展",
            "description": "本文介绍了深度学习和神经网络的最新技术发展，包括Transformer架构、大语言模型训练技巧、以及在实际应用中的部署优化方案。",
            "category": "AI"
        },
        {
            "title": "OpenAI GPT-4技术报告解读",
            "description": "详细解读OpenAI发布的GPT-4技术报告，分析其架构设计、训练方法、能力评估，以及对人工智能领域的影响和未来发展方向。",
            "category": "papers"
        },
        {
            "title": "Claude Code编程助手实战指南",
            "description": "分享使用Claude Code进行编程开发的实战经验，包括代码生成、调试、重构、文档编写等功能的最佳实践和使用技巧。",
            "category": "tools"
        }
    ]

    print("🧪 开始测试封面生成...")
    print()

    success_count = 0
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 测试用例 {i}: {test_case['title']}")
        print(f"   描述: {test_case['description'][:100]}...")
        print(f"   分类: {test_case['category']}")

        # 生成prompt预览
        prompt = generator._optimize_description(
            test_case['description'],
            test_case['title'],
            test_case['category']
        )
        print(f"   Prompt: {prompt[:150]}...")

        # 实际生成图片
        print("   🎨 正在生成图片...")
        image_url = generator.generate_cover(
            title=test_case['title'],
            description=test_case['description'],
            category=test_case['category'],
            force=True  # 强制重新生成
        )

        if image_url:
            print(f"   ✅ 生成成功: {image_url}")
            success_count += 1
        else:
            print("   ❌ 生成失败")

        print()

    # 总结
    print("📊 测试结果总结:")
    print(f"   - 总测试用例: {len(test_cases)}")
    print(f"   - 成功生成: {success_count}")
    print(f"   - 失败数量: {len(test_cases) - success_count}")
    print(f"   - 成功率: {success_count/len(test_cases)*100:.1f}%")

    if success_count == len(test_cases):
        print("🎉 所有测试用例都成功生成了封面图片！")
        return True
    else:
        print("⚠️  部分测试用例失败，请检查日志")
        return False

def test_prompt_optimization():
    """测试prompt优化功能"""
    print("\n🔍 测试Prompt优化功能")
    print("=" * 30)

    generator = CoverImageGenerator()

    test_text = """
    本文详细介绍了ChatGPT的最新技术进展，包括GPT-4架构的改进、多模态能力的增强、
    在编程和创作领域的应用，以及如何使用API进行开发集成。同时讨论了AI技术的
    伦理问题和未来发展趋势。
    """

    # 测试关键词提取
    keywords = generator._extract_keywords(test_text, "ChatGPT技术进展")
    print(f"提取的关键词: {keywords}")

    # 测试prompt生成
    prompt = generator._optimize_description(test_text, "ChatGPT技术进展", "AI")
    print(f"生成的Prompt: {prompt}")
    print()

    return True

if __name__ == "__main__":
    print("🚀 开始测试改进后的AI封面生成功能")
    print()

    # 测试prompt优化
    test_prompt_optimization()

    # 测试实际生成
    success = test_cover_generation()

    if success:
        print("\n🎯 所有测试完成！新的封面生成功能已准备就绪。")
        print("\n💡 使用建议:")
        print("   - 图片尺寸: 1200x630 (横屏16:9比例)")
        print("   - 样式特点: 几何抽象、无文字、无人物")
        print("   - 适用场景: 博客文章卡片头部")
        print("   - 生成命令: python scripts/generate_covers_for_directory.py papers")
    else:
        print("\n❌ 部分测试失败，请检查配置和网络连接")

    sys.exit(0 if success else 1)