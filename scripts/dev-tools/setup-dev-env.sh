#!/bin/bash
# Hugo博客开发环境设置脚本

set -e

echo "🚀 设置Hugo博客开发环境..."

# 检查是否安装了uv
if ! command -v uv &> /dev/null; then
    echo "❌ 未找到uv，请先安装uv:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 检查是否安装了conda（可选）
CONDA_AVAILABLE=false
if command -v conda &> /dev/null; then
    CONDA_AVAILABLE=true
    echo "✅ 检测到conda环境"
fi

# 创建虚拟环境
echo "📦 创建Python虚拟环境..."
if [ "$CONDA_AVAILABLE" = true ]; then
    # 使用conda创建环境
    echo "使用conda创建环境: blog-tools"
    conda create -n blog-tools python=3.11 -y
    conda activate blog-tools
else
    # 使用uv创建虚拟环境
    echo "使用uv创建虚拟环境..."
    uv venv .venv
    source .venv/bin/activate
fi

# 安装工具依赖
echo "📦 安装工具依赖..."
cd tools/image-optimization
uv pip install -r requirements.txt
cd ../..

# 验证安装
echo "✅ 验证安装..."
python --version
python -c "import PIL; print(f'PIL版本: {PIL.__version__}')"

echo ""
echo "🎉 开发环境设置完成！"
echo ""
echo "使用方法:"
if [ "$CONDA_AVAILABLE" = true ]; then
    echo "  conda activate blog-tools"
else
    echo "  source .venv/bin/activate"
fi
echo ""
echo "然后运行:"
echo "  make dev              # 启动开发服务器"
echo "  make optimize-images  # 优化图片"
echo "  make analyze-performance  # 分析性能"
