#!/bin/bash
#
# 安装 Git hooks
# 这个脚本会创建 pre-commit hook 来自动更新博客字数统计
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ 错误: .git/hooks 目录不存在"
    echo "   请确保您在 Git 仓库根目录下运行此脚本"
    exit 1
fi

# 创建 pre-commit hook
HOOK_FILE="$HOOKS_DIR/pre-commit"
cat > "$HOOK_FILE" << 'HOOK_EOF'
#!/bin/bash
#
# Git pre-commit hook: 自动更新博客文章的字数和阅读时间统计
# 仅在提交包含 .md 文件时运行
#

# 获取暂存区中修改的 .md 文件
STAGED_MD_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$' | grep '^content/')

if [ -z "$STAGED_MD_FILES" ]; then
    # 没有需要处理的 .md 文件，直接退出
    exit 0
fi

echo "📊 检测到 Markdown 文件变更，开始更新字数和阅读时间统计..."
echo ""

# 检查 Python 和 PyYAML
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "⚠️  警告: 未找到 python 命令，跳过字数统计更新"
    exit 0
fi

# 使用 python3 如果 python 不存在
PYTHON_CMD=$(command -v python3 || command -v python)

# 运行更新脚本
if [ -f "scripts/update_word_count.py" ]; then
    $PYTHON_CMD scripts/update_word_count.py --update $STAGED_MD_FILES
    
    if [ $? -eq 0 ]; then
        # 如果有文件被更新，将它们添加到暂存区
        UPDATED_FILES=$(git diff --name-only | grep '\.md$')
        if [ -n "$UPDATED_FILES" ]; then
            echo ""
            echo "📝 已将更新的文件添加到暂存区"
            echo "$UPDATED_FILES" | xargs git add
        fi
    fi
else
    echo "⚠️  警告: 未找到 scripts/update_word_count.py"
fi

exit 0
HOOK_EOF

chmod +x "$HOOK_FILE"

echo "✅ Git pre-commit hook 已安装"
echo ""
echo "📋 Hook 功能："
echo "   - 自动检测提交的 Markdown 文件"
echo "   - 计算中文字数和阅读时间"
echo "   - 更新 front matter 中的 wordCount 和 readingTime"
echo "   - 自动将更新后的文件添加到暂存区"
echo ""
echo "💡 提示:"
echo "   如果不想运行 hook，可以使用: git commit --no-verify"

