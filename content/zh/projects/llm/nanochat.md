

项目基本信息
名称: nanochat - "最便宜的$100 ChatGPT克隆"
用途: 完整的LLM训练和推理流程，从数据到Web UI
规模: ~8K行代码，45个文件，单个 8XH100 节点上 4 小时完成训练
成本: ~$100 (d20 模型，561M 参数)
🛠️ 技术栈
Python 3.10+ + PyTorch 2.8+
Rust tokenizer (rustbpe via PyO3)
FastAPI + Uvicorn 用于 Web 服务
HuggingFace datasets + wandb 实验追踪
uv 作为依赖管理器