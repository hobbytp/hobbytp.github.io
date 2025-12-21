.PHONY: dev build clean stop optimize-images analyze-performance build-measure analyze-content analyze-content-ai full-build full-build-ai validate-architecture generate-covers generate-ai-covers generate-cover-from-photo test-covers generate-covers-for-directory ingest-data help

# Shell 设置
# 让每个配方(target)的所有命令在同一个 shell 中执行，确保 .env 中的导出变量可在后续命令中生效
.ONESHELL:
SHELL := bash
.SHELLFLAGS := -c

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

# 测量构建时间
build-measure:
	@echo "⏱️  测量Hugo构建时间..."
	@start_time=$$(date +%s); \
	$(MAKE) build; \
	end_time=$$(date +%s); \
	duration=$$((end_time - start_time)); \
	echo "✅ 构建完成，耗时: $${duration} 秒"

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
	# 加载 .env 以提供 AI 所需的密钥（如 GEMINI、OPENAI、MODELSCOPE 等）
	set -a; \
	if [ -f .env ]; then . .env; echo "Environment variables loaded from .env"; else echo "No .env file found, using environment variables"; fi; \
	set +a; \
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
	# 加载 .env 以提供 AI 所需的密钥
	set -a; \
	if [ -f .env ]; then . .env; echo "Environment variables loaded from .env"; else echo "No .env file found, using environment variables"; fi; \
	set +a; \
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
full-build: validate-architecture optimize-images analyze-content build analyze-performance

# 🤖 AI增强完整构建流程
full-build-ai: validate-architecture optimize-images analyze-content-ai build analyze-performance

# 清理生成的文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf public/ resources/_gen/ static/images/optimized/ static/images/backup/
	docker-compose down -v

# 更新主题
update-theme:
	@echo "📦 更新Hugo主题..."
	git submodule update --init --recursive

# 验证架构完整性
validate-architecture:
	@echo "🔍 验证Hugo架构完整性..."
	@./scripts/validate-architecture.sh

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

# 生成AI封面图片（使用Hugo原生CSS方式，无需API）
generate-covers:
	@echo "🎨 为文章生成AI封面..."
	@echo "使用Hugo原生CSS生成，无需外部API"
	@echo ""
	@echo "✅ AI封面系统已集成到文章卡片模板中"
	@echo "📝 系统会根据文章的title和description自动生成"
	@echo "🎭 支持分类特定配色和动画效果"
	@echo ""
	@echo "🔧 配置说明:"
	@echo "  - 自动检测文章的title和description字段"
	@echo "  - 基于内容哈希生成唯一封面样式"
	@echo "  - 支持深色/浅色主题自适应"
	@echo "  - 响应式设计，适配移动端"
	@echo ""
	@echo "💡 如需手动添加封面图片，在文章front matter中添加:"
	@echo "cover:"
	@echo "  image: \"/path/to/image.jpg\""
	@echo "  alt: \"文章标题\""

# 使用AI API生成真实封面图片
generate-ai-covers:
	@echo "🤖 Using AI API to generate real cover images..."
	@echo ""
	@echo "📋 Supported AI services:"
	@echo "  - Volcengine Jimeng (default, recommended in China)"
	@echo "  - ModelScope Qwen-image"
	@echo "  - OpenAI DALL-E (requires VPN)"
	@echo ""
	@echo "🔑 Environment variables:"
	@echo "  # Volcengine (default):"
	@echo "  export VOLCENGINE_ACCESS_KEY=\"your-access-key\""
	@echo "  export VOLCENGINE_SECRET_KEY=\"your-secret-key\""
	@echo "  export TEXT2IMAGE_PROVIDER=\"volcengine\"  # optional, volcengine is default"
	@echo ""
	@echo "  # ModelScope:"
	@echo "  export MODELSCOPE_API_KEY=\"your-modelscope-key\""
	@echo "  export TEXT2IMAGE_PROVIDER=\"modelscope\""
	@echo ""
	@echo "  # OpenAI:"
	@echo "  export OPENAI_API_KEY=\"your-openai-key\""
	@echo "  export TEXT2IMAGE_PROVIDER=\"openai\""
	@echo ""
	@echo "🚀 Execute generation:"
	@bash -lc '\
	  set -a; \
	  if [ -f .env ]; then . .env; echo "Environment variables loaded from .env"; else echo "No .env file found, using environment variables"; fi; \
	  set +a; \
	  if ([ -n "$$VOLCENGINE_ACCESS_KEY" ] && [ -n "$$VOLCENGINE_SECRET_KEY" ]) || [ -n "$$MODELSCOPE_API_KEY" ] || [ -n "$$OPENAI_API_KEY" ]; then \
	    echo "Starting AI cover generation..."; \
	    $(PYTHON_CMD) scripts/ai_cover_generator.py; \
	    echo "✅ AI cover generation completed!"; \
	  else \
	    echo "⚠️  警告: 未设置必要的API密钥环境变量"; \
	    echo "请在 .env 文件中添加以下任一配置:"; \
	    echo ""; \
	    echo "  # Volcengine (默认):"; \
	    echo "  VOLCENGINE_ACCESS_KEY=your-access-key"; \
	    echo "  VOLCENGINE_SECRET_KEY=your-secret-key"; \
	    echo ""; \
	    echo "  # 或 ModelScope:"; \
	    echo "  MODELSCOPE_API_KEY=your-key"; \
	    echo "  TEXT2IMAGE_PROVIDER=modelscope"; \
	    echo ""; \
	    echo "  # 或 OpenAI:"; \
	    echo "  OPENAI_API_KEY=your-key"; \
	    echo "  TEXT2IMAGE_PROVIDER=openai"; \
	  fi'

# 用现成照片生成封面（无需 AI API）
generate-cover-from-photo:
	@bash -lc '\
	  if [ -z "$(FILE)" ] || [ -z "$(PHOTO)" ]; then \
	    echo "❌ 用法: make generate-cover-from-photo FILE=content/zh/xxx.md PHOTO=path/to/photo.jpg [FORCE=true]"; \
	    exit 1; \
	  fi; \
	  FORCE_FLAG=""; \
	  if [ "$(FORCE)" = "true" ] || [ "$(FORCE)" = "1" ]; then FORCE_FLAG="--force"; fi; \
	  echo "🖼️  Using existing photo to generate cover..."; \
	  $(PYTHON_CMD) scripts/ai_cover_generator.py --specific-file "$(FILE)" --photo "$(PHOTO)" $$FORCE_FLAG; \
	  echo "✅ Photo cover generation completed!"; \
	'

# 测试封面生成效果
test-covers:
	@echo "🧪 测试封面生成效果..."
	@echo ""
	@echo "启动开发服务器查看效果:"
	@echo "  make dev"
	@echo ""
	@echo "🎯 测试要点:"
	@echo "  1. 查看没有手动封面的文章是否显示AI生成的封面"
	@echo "  2. 测试不同分类文章的配色差异"
	@echo "  3. 验证深色/浅色主题切换效果"
	@echo "  4. 检查鼠标悬停动画是否正常"
	@echo "  5. 确认文字可读性（对比度、阴影）"
	@echo ""
	@echo "🔧 如果需要优化封面样式，编辑以下文件:"
	@echo "  - layouts/_default/cover-image.html (封面模板)"
	@echo "  - assets/css/custom.css (样式调整)"

# 为指定目录生成AI封面
generate-covers-for-directory:
	@bash -lc '\
	  if [ -z "$(DIRECTORY)" ]; then \
	    echo "❌ 请指定目录名称: make generate-covers-for-directory DIRECTORY=papers"; \
	    echo ""; \
	    echo "📁 可用目录:"; \
	    $(PYTHON_CMD) scripts/generate_covers_for_directory.py --list-directories; \
	    exit 1; \
	  fi; \
	  echo "🎯 为目录 '\''$(DIRECTORY)'\'' 生成AI封面..."; \
	  set -a; \
	  if [ -f .env ]; then . .env; echo "Environment variables loaded from .env"; else echo "No .env file found, using environment variables"; fi; \
	  set +a; \
	  RECURSIVE_FLAG="--recursive"; \
	  if [ "$(NO_RECURSIVE)" = "true" ] || [ "$(NO_RECURSIVE)" = "1" ]; then RECURSIVE_FLAG="--no-recursive"; fi; \
	  FORCE_FLAG=""; \
	  if [ "$(FORCE)" = "true" ] || [ "$(FORCE)" = "1" ]; then FORCE_FLAG="--force"; fi; \
	  DRY_RUN_FLAG=""; \
	  if [ "$(DRY_RUN)" = "true" ] || [ "$(DRY_RUN)" = "1" ]; then DRY_RUN_FLAG="--dry-run"; fi; \
	  if ([ -n "$$VOLCENGINE_ACCESS_KEY" ] && [ -n "$$VOLCENGINE_SECRET_KEY" ]) || [ -n "$$MODELSCOPE_API_KEY" ] || [ -n "$$OPENAI_API_KEY" ]; then \
	    echo "Starting AI cover generation for directory: $(DIRECTORY)..."; \
	    $(PYTHON_CMD) scripts/generate_covers_for_directory.py $(DIRECTORY) $$RECURSIVE_FLAG $$FORCE_FLAG $$DRY_RUN_FLAG; \
	    echo "✅ AI cover generation completed for directory: $(DIRECTORY)!"; \
	  else \
	    echo "⚠️  警告: 未设置必要的API密钥环境变量"; \
	    echo "请在 .env 文件中添加以下任一配置:"; \
	    echo ""; \
	    echo "  # Volcengine (默认):"; \
	    echo "  VOLCENGINE_ACCESS_KEY=your-access-key"; \
	    echo "  VOLCENGINE_SECRET_KEY=your-secret-key"; \
	    echo ""; \
	    echo "  # 或 ModelScope:"; \
	    echo "  MODELSCOPE_API_KEY=your-key"; \
	    echo "  TEXT2IMAGE_PROVIDER=modelscope"; \
	    echo ""; \
	    echo "  # 或 OpenAI:"; \
	    echo "  OPENAI_API_KEY=your-key"; \
	    echo "  TEXT2IMAGE_PROVIDER=openai"; \
	  fi'

# RAG数据摄取
ingest-data:
	@bash scripts/ingest.sh "$(FILE)" "$(FORCE)" "$(ENV_FILE)"

# 帮助信息
help:
	@echo "Hugo Blog Management Tool"
	@echo ""
	@echo "🚨 Architecture Validation:"
	@echo "  make validate-architecture  Validate architecture integrity (Run before commit)"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev              Start Hugo development server"
	@echo "  make fresh            Clean and restart development server"
	@echo "  make stop             Stop Hugo service"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build            Execute production build"
	@echo "  make build-measure    Measure build time"
	@echo "  make full-build       Full build process (validate + optimize + analyze)"
	@echo "  make full-build-ai    🤖 AI-enhanced full build process"
	@echo "  make clean            Clean build files"
	@echo ""
	@echo "Optimization Tools:"
	@echo "  make optimize-images  Optimize image resources"
	@echo "  make test-images      Test image optimization (preview mode)"
	@echo "  make analyze-performance  Analyze Hugo performance"
	@echo "  make performance-report   Generate performance report"
	@echo "  make analyze-content      Analyze content quality"
	@echo "  make analyze-content-ai   🤖 AI-enhanced content analysis"
	@echo "  make generate-json-data   Generate JSON data (frontend dashboard)"
	@echo "  make generate-json-data-ai 🤖 Generate AI-enhanced JSON data"
	@echo "  make analyze-content FILE=path/to/file.md     Analyze single file"
	@echo "  make analyze-content-ai FILE=path/to/file.md  🤖 AI-enhanced single file analysis"
	@echo "  make export-pdf          Export PDF"
	@echo "  make export-pdf FILE=path/to/file.md         Export single file PDF"
	@echo ""
	@echo "Cover Images:"
	@echo "  make generate-covers    Generate CSS art covers (No API required)"
	@echo "  make generate-ai-covers Generate real images using AI API"
	@echo "  make generate-cover-from-photo FILE=path PHOTO=path [FORCE=true]  Use an existing photo as cover"
	@echo "  make test-covers        Test cover generation"
	@echo "  make generate-covers-for-directory DIRECTORY=dir [FORCE=true DRY_RUN=true NO_RECURSIVE=true]  Generate AI covers for directory"
	@echo ""
	@echo "RAG Data Ingestion:"
	@echo "  make ingest-data       Ingest all blog content to Vectorize"
	@echo "  make ingest-data FILE=path/to/file.md  Ingest single file"
	@echo "  make test-ingest       Run ingest pipeline unit tests"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make update-theme     Update Hugo theme"
	@echo "  make install-tools    Install tool dependencies"
	@echo "  make help             Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make install-tools    # Install dependencies for first use"
	@echo "  make fresh           # Clean and start dev environment"
	@echo "  make full-build      # Execute full build process"
	@echo "  make generate-json-data   # Generate dashboard data"
	@echo "  make generate-json-data-ai # Generate AI-enhanced dashboard data"
	@echo "  make analyze-content FILE=./content/zh/google/a2a.md  # Analyze single file"
	@echo "  make analyze-content-ai FILE=./content/zh/google/a2a.md # AI-enhanced analysis"
	@echo "  make export-pdf FILE=./content/zh/google/a2a.md       # Export single file PDF"

# Run ingest unit tests via uv + venv
test-ingest:
	@echo "Running ingest unit tests via uv + venv"
	@if command -v uv >/dev/null 2>&1; then \
		uv run python -m unittest scripts/test_ingest.py; \
	else \
		python -m unittest scripts/test_ingest.py; \
	fi

# Vectorize metadata index creation (category as filterable field)
CF_VECTOR_INDEX ?= blog-index-m3

.PHONY: vectorize-create-category-index
vectorize-create-category-index:
	@echo "Creating filterable metadata index 'category' on $(CF_VECTOR_INDEX)"
	@npx wrangler vectorize create-metadata-index $(CF_VECTOR_INDEX) --property-name=category --type=string

