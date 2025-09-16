FROM hugomods/hugo:latest

# 设置工作目录
WORKDIR /src

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 1313

# 设置默认命令
CMD ["server", "--bind", "0.0.0.0", "-D"] 