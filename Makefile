.PHONY: dev build clean

# 开发环境
dev:
	docker-compose up hugo

# 生产环境构建
build:
	docker-compose run --rm hugo-build

# 清理生成的文件
clean:
	rm -rf public/ resources/_gen/
	docker-compose down -v

# 更新主题
update-theme:
	git submodule update --init --recursive

# 启动新的开发会话（清理后启动）
fresh: clean dev 