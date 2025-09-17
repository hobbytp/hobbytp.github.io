#!/bin/bash

# Hugo SPA模式切换脚本
# 用于在传统多页面模式和SPA模式之间切换

set -e

SPA_MODE=${1:-"enable"}

echo "🚀 Hugo SPA模式切换工具"
echo "================================"

if [ "$SPA_MODE" = "enable" ]; then
    echo "📱 启用SPA模式..."
    
    # 备份原始文件
    if [ ! -f "layouts/_default/baseof.html.backup" ]; then
        cp layouts/_default/baseof.html layouts/_default/baseof.html.backup
        echo "✅ 已备份原始 baseof.html"
    fi
    
    if [ ! -f "layouts/_default/list.html.backup" ]; then
        cp layouts/_default/list.html layouts/_default/list.html.backup
        echo "✅ 已备份原始 list.html"
    fi
    
    if [ ! -f "layouts/_default/single.html.backup" ]; then
        cp layouts/_default/single.html layouts/_default/single.html.backup 2>/dev/null || echo "⚠️  未找到 single.html，将创建新文件"
    fi
    
    # 切换到SPA模式
    cp layouts/_default/baseof-spa.html layouts/_default/baseof.html
    cp layouts/_default/list-spa.html layouts/_default/list.html
    cp layouts/_default/single-spa.html layouts/_default/single.html
    
    echo "✅ 已应用SPA模板文件"
    
    echo "✅ SPA模式已启用"
    echo ""
    echo "🎨 新功能特性："
    echo "   • 固定左侧导航栏"
    echo "   • 卡片式文章展示"
    echo "   • 无刷新页面切换"
    echo "   • 文章页面右侧目录"
    echo "   • 搜索和筛选功能"
    echo "   • 响应式设计"
    echo ""
    echo "🌐 访问地址: http://localhost:1313"
    
elif [ "$SPA_MODE" = "disable" ]; then
    echo "📄 恢复传统模式..."
    
    # 恢复原始文件
    if [ -f "layouts/_default/baseof.html.backup" ]; then
        cp layouts/_default/baseof.html.backup layouts/_default/baseof.html
        echo "✅ 已恢复原始 baseof.html"
    fi
    
    if [ -f "layouts/_default/list.html.backup" ]; then
        cp layouts/_default/list.html.backup layouts/_default/list.html
        echo "✅ 已恢复原始 list.html"
    fi
    
    if [ -f "layouts/_default/single.html.backup" ]; then
        cp layouts/_default/single.html.backup layouts/_default/single.html
        echo "✅ 已恢复原始 single.html"
    fi
    
    echo "✅ 传统模式已恢复"
    echo ""
    echo "📝 传统模式特性："
    echo "   • 标准多页面导航"
    echo "   • 更好的SEO支持"
    echo "   • 浏览器历史记录支持"
    echo "   • 直接链接访问"
    
else
    echo "❌ 无效参数: $SPA_MODE"
    echo ""
    echo "使用方法:"
    echo "  $0 enable   - 启用SPA模式"
    echo "  $0 disable  - 禁用SPA模式"
    echo "  $0 status   - 查看当前模式"
    exit 1
fi

if [ "$SPA_MODE" = "status" ]; then
    echo "📊 当前模式状态:"
    echo "================================"
    
    if grep -q "BlogSPA" layouts/_default/baseof.html 2>/dev/null; then
        echo "🟢 当前模式: SPA模式"
        echo "   • 固定侧边栏: ✅"
        echo "   • 卡片布局: ✅"
        echo "   • AJAX加载: ✅"
    else
        echo "🔵 当前模式: 传统模式"
        echo "   • 多页面导航: ✅"
        echo "   • 标准布局: ✅"
    fi
fi

echo ""
echo "🔄 重启Hugo服务器以应用更改..."
echo "   运行: docker-compose restart hugo"
