.PHONY: dev build clean stop optimize-images analyze-performance analyze-content analyze-content-ai full-build full-build-ai help

# 默认目标
.DEFAULT_GOAL := help

# Python命令配置（优先使用conda news_collector环境）
PYTHON_CMD := $(shell \
	if [ -n "$$CONDA_DEFAULT_ENV" ] && [ "$$CONDA_DEFAULT_ENV" = "news_collector" ]; then \
		echo "python"; \
	else \
		echo "conda run -n news_collector python"; \
	fi \
)

# 开发环境
dev:
	@echo "🚀 启动Hugo开发服务器..."
	docker-compose up hugo

# 生产环境构建
build:
	@echo "🔨 执行Hugo生产构建..."
	docker-compose run --rm hugo-build

# 优化图片
optimize-images:
	@echo "🖼️  优化图片资源..."
	@cd tools/image-optimization && $(PYTHON_CMD) image_optimizer.py --input-dir ../../static/images --output-dir ../../static/images/optimized

# 分析性能
analyze-performance:
	@echo "📊 分析Hugo性能..."
	@cd tools/performance-monitor && $(PYTHON_CMD) performance_analyzer.py --all

# 分析内容质量
analyze-content:
	@echo "📝 分析内容质量..."
	@if [ -n "$(FILE)" ]; then \
		echo "分析单个文件: $(FILE)"; \
		cd tools/content-analysis && $(PYTHON_CMD) content_analyzer.py --analyze-single "$(FILE)"; \
	else \
		cd tools/content-analysis && $(PYTHON_CMD) content_analyzer.py --input-dir ../..; \
	fi

# 🤖 AI增强内容分析
analyze-content-ai:
	@echo "🤖 AI增强内容分析..."
	@if [ -n "$(FILE)" ]; then \
		echo "🤖 AI增强分析单个文件: $(FILE)"; \
		cd tools/content-analysis && $(PYTHON_CMD) content_analyzer.py --analyze-single "$(FILE)" --ai-enhance; \
	else \
		cd tools/content-analysis && $(PYTHON_CMD) content_analyzer.py --input-dir ../.. --ai-enhance; \
	fi

# 生成JSON数据（供前端仪表板使用）
generate-json-data:
	@echo "📊 生成分析JSON数据..."
	@cd tools/content-analysis && $(PYTHON_CMD) content_analyzer.py --input-dir ../.. --json-data
	@cp tools/content-analysis/content-analysis-data.json static/

# 🤖 生成AI增强JSON数据
generate-json-data-ai:
	@echo "🤖 生成AI增强分析JSON数据..."
	@cd tools/content-analysis && $(PYTHON_CMD) content_analyzer.py --input-dir ../.. --json-data --ai-enhance
	@cp tools/content-analysis/content-analysis-data.json static/

# 导出PDF
export-pdf:
	@echo "📄 导出PDF..."
	@if [ -n "$(FILE)" ]; then \
		echo "导出单个文件PDF: $(FILE)"; \
		cd tools/pdf-exporter && $(PYTHON_CMD) pdf_exporter.py --article "$(FILE)" --serve-url http://localhost:1313; \
	else \
		cd tools/pdf-exporter && $(PYTHON_CMD) pdf_exporter.py --all --input-dir ../.. --serve-url http://localhost:1313; \
	fi


# 完整构建流程（优化图片 + 内容分析 + 构建 + 性能分析）
full-build: optimize-images analyze-content build analyze-performance

# 🤖 AI增强完整构建流程
full-build-ai: optimize-images analyze-content-ai build analyze-performance

# 清理生成的文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf public/ resources/_gen/ static/images/optimized/ static/images/backup/
	docker-compose down -v

# 更新主题
update-theme:
	@echo "📦 更新Hugo主题..."
	git submodule update --init --recursive

# 启动新的开发会话（清理后启动）
fresh: clean dev

# 停止正在运行的服务（不移除容器与卷）
stop:
	@echo "⏹️  停止Hugo服务..."
	docker-compose stop

# 测试图片优化（不实际执行）
test-images:
	@echo "🧪 测试图片优化..."
	@cd tools/image-optimization && $(PYTHON_CMD) image_optimizer.py --dry-run --input-dir ../../static/images

# 生成性能报告
performance-report:
	@echo "📈 生成性能报告..."
	@cd tools/performance-monitor && $(PYTHON_CMD) performance_analyzer.py --generate-report

# 安装工具依赖
install-tools:
	@echo "📦 安装工具依赖..."
	@if [ -n "$$CONDA_DEFAULT_ENV" ]; then \
		echo "使用conda环境安装依赖..."; \
		conda install -c conda-forge pillow -y; \
	else \
		echo "使用uv安装依赖..."; \
		uv venv .venv 2>/dev/null || true; \
		source .venv/bin/activate && uv pip install -r tools/image-optimization/requirements.txt; \
	fi
	@echo "✅ 工具依赖安装完成"

# 帮助信息
help:
	@echo "Hugo博客管理工具"
	@echo ""
	@echo "开发命令:"
	@echo "  make dev              启动Hugo开发服务器"
	@echo "  make fresh            清理后重新启动开发服务器"
	@echo "  make stop             停止Hugo服务"
	@echo ""
	@echo "构建命令:"
	@echo "  make build            执行生产环境构建"
	@echo "  make full-build       完整构建流程（图片优化+构建+分析）"
	@echo "  make full-build-ai    🤖 AI增强完整构建流程"
	@echo "  make clean            清理构建文件"
	@echo ""
	@echo "优化工具:"
	@echo "  make optimize-images  优化图片资源"
	@echo "  make test-images      测试图片优化（预览模式）"
	@echo "  make analyze-performance  分析Hugo性能"
	@echo "  make performance-report   生成性能报告"
	@echo "  make analyze-content      分析内容质量"
	@echo "  make analyze-content-ai   🤖 AI增强内容分析"
	@echo "  make generate-json-data   生成JSON数据（前端仪表板）"
	@echo "  make generate-json-data-ai 🤖 生成AI增强JSON数据"
	@echo "  make analyze-content FILE=path/to/file.md     分析单个文件"
	@echo "  make analyze-content-ai FILE=path/to/file.md  🤖 AI增强分析单个文件"
	@echo "  make export-pdf          导出PDF"
	@echo "  make export-pdf FILE=path/to/file.md         导出单个文件PDF"
	@echo ""
	@echo "维护命令:"
	@echo "  make update-theme     更新Hugo主题"
	@echo "  make install-tools    安装工具依赖"
	@echo "  make help             显示此帮助信息"
	@echo ""
	@echo "示例:"
	@echo "  make install-tools    # 首次使用时安装依赖"
	@echo "  make fresh           # 清理并启动开发环境"
	@echo "  make full-build      # 执行完整构建流程"
	@echo "  make generate-json-data   # 生成前端仪表板数据"
	@echo "  make generate-json-data-ai # 生成AI增强仪表板数据"
	@echo "  make analyze-content FILE=./content/zh/google/a2a.md  # 分析单个文件"
	@echo "  make analyze-content-ai FILE=./content/zh/google/a2a.md # AI增强分析"
	@echo "  make export-pdf FILE=./content/zh/google/a2a.md       # 导出单个文件PDF"