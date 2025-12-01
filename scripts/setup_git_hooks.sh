#!/bin/bash
#
# 安装 Git hooks
# 这个脚本会创建 pre-commit hook 来自动更新博客字数统计
# 以及 pre-push hook 来验证架构完整性
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
echo ""

# 创建 pre-push hook
PUSH_HOOK_FILE="$HOOKS_DIR/pre-push"
cat > "$PUSH_HOOK_FILE" << 'PUSH_HOOK_EOF'
#!/bin/bash
#
# Git pre-push hook: 验证 Hugo 架构完整性
# 在推送前运行架构验证，确保代码符合规范
#

# 检查是否有需要推送的提交
# pre-push hook 接收参数: <remote> <url>
# 通过 stdin 接收: <local ref> <local sha1> <remote ref> <remote sha1>

remote="$1"
url="$2"

# 读取 stdin 检查是否有实际的推送内容
has_commits=0
while read local_ref local_sha remote_ref remote_sha
do
    if [ "$local_sha" != "0000000000000000000000000000000000000000" ]; then
        has_commits=1
        break
    fi
done

# 如果没有新的提交要推送，直接退出
if [ $has_commits -eq 0 ]; then
    exit 0
fi

echo ""
echo "🔍 开始 pre-push 架构验证..."
echo ""

# 运行架构验证脚本
if [ -f "scripts/validate-architecture.sh" ]; then
    ./scripts/validate-architecture.sh
    VALIDATION_RESULT=$?
    
    if [ $VALIDATION_RESULT -ne 0 ]; then
        echo ""
        echo "❌ 架构验证失败，push 已中止"
        echo "   请修复上述问题后再推送"
        echo "   或使用 git push --no-verify 跳过验证"
        exit 1
    fi
else
    echo "⚠️  警告: 未找到 scripts/validate-architecture.sh"
    echo "   跳过架构验证"
fi

echo ""
echo "✅ 架构验证通过，继续推送..."
echo ""

exit 0
PUSH_HOOK_EOF

chmod +x "$PUSH_HOOK_FILE"

echo "✅ Git pre-push hook 已安装"
echo ""
echo "📋 Pre-push Hook 功能："
echo "   - 验证 CSS 文件行数限制"
echo "   - 检查模板架构合规性"
echo "   - 验证 Hugo 构建（带30秒超时）"
echo "   - 防止不符合规范的代码被推送"
echo ""
echo "💡 提示:"
echo "   如果不想运行验证，可以使用: git push --no-verify"
