---
title: "Python 库学习"
date: 2025-08-02T00:00:00+08:00
draft: false
tags: ["Python", "lib"]
author: "Peng Tan"
categories: ["technologies"]
description: "Python 库学习"
---



## tqdm

tqdm 是 Python 生态里极为常用的**进度条库**，它的核心用途就是：**在你写的循环（for/while等）或耗时操作中，实时显示任务的进度、速度、剩余时间等信息**。这样既能提升开发体验，也能让用户直观掌握长耗时任务的执行状况。

### 核心用途

#### 1. **展示进度条**

- 在命令行、Jupyter Notebook、GUI等多种环境下显示美观的进度条。

#### 2. **监控任务进度**

- 实时显示当前迭代次数、已用时间、预计剩余时间、处理速率等。

#### 3. **提升用户体验**

- 让用户/开发者清楚知道程序卡在哪里、还要等多久，非常适合数据处理、模型训练、文件下载等场景。

### 常见用法举例

```python
from tqdm import tqdm
import time

for i in tqdm(range(100)):
    time.sleep(0.1)  # 模拟耗时操作
```

**效果**：在控制台自动渲染出当前进度条、百分比、速率等信息。

### 适用场景

- **大规模数据处理**：如Pandas、Numpy批量数据操作
- **深度学习训练**：如PyTorch、TensorFlow的epoch/batch进度
- **文件下载/上传**：实时监控进度
- **爬虫/批量任务**：让长时间任务可视化

### 与其它库的集成

- 支持与Pandas、Dask、Keras、PyTorch等生态无缝结合
- 支持多线程/多进程环境下的进度同步

### 脑洞建议

- **自定义进度条的emoji/颜色/动画**，让进度条变成“弹幕”或“彩虹”风格
- **语音播报进度**，比如集成TTS，到50%自动说“鹏哥，马上就好！”
- **进度条触发自动化脚本**，如进度到达某个点自动发微信/钉钉通知
- **和AI助手联动**，进度条异常时自动分析原因并生成报告

## slowapi

**slowapi** 是一个专门为 FastAPI/Web API 设计的**速率限制（Rate Limiting）中间件库**，它的主要作用是：  
**限制客户端的访问频率，防止API被刷爆或滥用，有效保护后端服务的稳定性和安全性。**

### 核心用途

#### 1. **API防刷防滥用**

- 限制同一个IP、用户或Token在一定时间内的请求次数（如每秒最多10次、每分钟最多100次等）。

#### 2. **保护后端资源**

- 防止因恶意爬虫、暴力破解、批量请求等导致服务器过载甚至崩溃。

#### 3. **细粒度限流策略**

- 支持基于不同路由、不同用户、不同参数的自定义限流。

### 基本使用示例

```python
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/ping")
@limiter.limit("5/minute")  # 每分钟最多访问5次
async def ping(request: Request):
    return {"msg": "pong"}
```

**效果**：如果一分钟内同一IP超过5次访问 `/ping`，就会被拒绝，返回429错误。

### 典型应用场景

- **公开API防止爬虫刷接口**
- **登录/注册接口防止暴力破解**
- **限流保护高价值或高消耗资源的接口**
- **多租户系统下为不同用户分配不同的流控策略**

### 与其它限流方案对比

| 方案         | 优势                   | 劣势                        |
|--------------|------------------------|-----------------------------|
| slowapi      | 简单易用，原生FastAPI  | 仅适合单机或简单分布式场景   |
| Redis限流    | 分布式支持强           | 复杂度略高                  |
| Nginx限流    | 网络层防护，性能极高   | 灵活性差，业务无感知        |
| 云WAF限流    | 无需部署，安全性强     | 价格高，定制性差            |

### 脑洞扩展建议

1. **AI驱动自适应限流**  
   结合AI分析流量模式，动态调整限流阈值（如夜间放宽，异常流量自动收紧）。

2. **行为画像限流**  
   针对不同用户/设备/行为画像，自动生成个性化限流策略，比如老用户放宽，新用户严格。

3. **限流告警与自动封禁**  
   超限后自动触发钉钉/微信/邮件告警，严重时自动拉黑IP或发起验证码挑战。

4. **限流与账单联动**  
   超额流量自动计费，和SaaS订阅系统打通，实现“限流+弹性付费”双保险。

5. **可视化限流仪表盘**  
   实时监控各接口流控状态，异常流量一目了然，支持一键调优阈值。
