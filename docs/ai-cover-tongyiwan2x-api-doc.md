通义万相-文生图模型基于文本生成图像，支持多种艺术风格与写实摄影效果，满足多样化创意需求。

快速入口：通义万相官网在线体验 ｜ 文生图使用指南

说明
通义万相官网的功能与API支持的能力可能存在差异。本文档以API的实际能力为准，并会随功能更新及时同步。

模型概览



模型名称

模型简介

输出图像格式

wan2.5-t2i-preview 推荐

万相2.5 preview

取消单边限制，在总像素面积与宽高比约束内，自由选尺寸

例如，支持768*2700，而2.2 及以下版本单边上限 1400
图像分辨率：总像素在[768*768, 1440*1440]之间

图像宽高比：[1:4, 4:1]
图像格式：png

wan2.2-t2i-flash 推荐

万相2.2极速版

较2.1模型速度提升50%

图像分辨率：宽高均在[512, 1440]像素之间

图像格式：png

wan2.2-t2i-plus 推荐

万相2.2专业版

较2.1模型稳定性与成功率全面提升

wanx2.1-t2i-turbo

万相2.1极速版

wanx2.1-t2i-plus

万相2.1专业版

wanx2.0-t2i-turbo

万相2.0极速版

说明
调用前，请查阅各地域支持的模型列表与价格。

前提条件
在调用前，先获取API Key，再配置API Key到环境变量。如需通过SDK进行调用，请安装DashScope SDK。

重要
北京和新加坡地域拥有独立的 API Key 与请求地址，不可混用，跨地域调用将导致鉴权失败或服务报错。

HTTP调用
由于文生图任务耗时较长（通常为1-2分钟），API采用异步调用。整个流程包含 “创建任务 -> 轮询获取” 两个核心步骤，具体如下：

具体耗时受限于排队任务数和服务执行情况，请在获取结果时耐心等待。
步骤1：创建任务获取任务ID
北京地域：POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis
新加坡地域(我不用！！！)：POST https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis

说明
创建成功后，使用接口返回的 task_id 查询结果，task_id 有效期为 24 小时。请勿重复创建任务，轮询获取即可。

新手指引请参见Postman。

请求参数
文生图文生图（使用反向提示词）
```bash
curl -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis \
    -H 'X-DashScope-Async: enable' \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
    -H 'Content-Type: application/json' \
    -d '{
    "model": "wan2.5-t2i-preview",
    "input": {
        "prompt": "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵",
        "negative_prompt": "人物"
    },
    "parameters": {
        "size": "1024*1024",
        "n": 1
    }
}' 
```

请求头（Headers）
Content-Type string （必选）

请求内容类型。此参数必须设置为application/json。

Authorization string（必选）

请求身份认证。接口使用阿里云百炼API-Key进行身份认证。示例值：Bearer sk-xxxx。

X-DashScope-Async string （必选）

异步处理配置参数。HTTP请求只支持异步，必须设置为enable。

重要
缺少此请求头将报错：“current user api does not support synchronous calls”。

请求体（Request Body）
model string （必选）

模型名称。示例值：wan2.5-t2i-preview。

各模型信息详见模型列表与价格。

input object （必选）

输入的基本信息，如提示词等。

属性

prompt string （必选）

正向提示词，用来描述生成图像中期望包含的元素和视觉特点。

支持中英文，每个汉字/字母占一个字符，超过部分会自动截断。长度限制因模型版本而异：

wan2.5-t2i-preview：长度不超过2000个字符。

wan2.2及以下版本模型：长度不超过800个字符。

示例值：一只坐着的橘黄色的猫，表情愉悦，活泼可爱，逼真准确。

提示词的使用技巧请参见文生图Prompt指南。

negative_prompt string （可选）

反向提示词，用来描述不希望在画面中看到的内容，可以对画面进行限制。

支持中英文，长度不超过500个字符，超过部分会自动截断。

示例值：低分辨率、错误、最差质量、低质量、残缺、多余的手指、比例不良等。

parameters object （可选）

图像处理参数。如设置图像分辨率、开启prompt智能改写、添加水印等。

属性

size string （可选）

输出图像的分辨率，格式为宽*高。默认值和约束因模型版本而异：

wan2.5-t2i-preview：默认值为 1280*1280。总像素在 [768*768, 1440*1440] 之间且宽高比范围为 [1:4, 4:1]。例如，768*2700符合要求。

wan2.2及以下版本模型：默认值为1024*1024。图像宽高在[512, 1440]之间，最大分辨率为1440*1440。例如， 768*2700超单边限制，不支持。

示例值：1280*1280。

常见比例推荐分辨率

1:1：1280*1280 或 1024*1024

2:3：800*1200

3:2：1200*800

3:4：960*1280

4:3：1280*960

9:16：720*1280

16:9：1280*720

21:9：1344*576

n integer （可选）

重要
n直接影响费用。费用 = 单价 × 图片张数，请在调用前确认模型价格。

生成图片的数量。取值范围为1~4张，默认为4。测试阶段建议设置为1，便于低成本验证。

prompt_extend boolean （可选）

是否开启prompt智能改写。开启后使用大模型对输入prompt进行智能改写。对于较短的prompt生成效果提升明显，但会增加耗时。

true：开启智能改写。

false：不开启智能改写。

该参数的默认值因模型版本而异：

wan2.5-t2i-preview：默认值为false。

wan2.2及以下版本模型：默认值为true。

示例值：true。

watermark boolean （可选）

是否添加水印标识，水印位于图片右下角，文案固定为“AI生成”。

false：默认值，不添加水印。

true：添加水印。

seed integer （可选）

随机数种子，取值范围是[0, 2147483647]。

如果不提供，则算法自动生成一个随机数作为种子。如果提供，则根据n的值分别为n张图片生成seed参数，例如n=4，算法将分别生成seed、seed+1、seed+2、seed+3作为参数的图片。

若需提升生成结果的可复现性，建议固定seed值。

请注意，由于模型生成具有概率性，即使使用相同 seed，也不能保证每次生成结果完全一致。

响应参数
成功响应
请保存 task_id，用于查询任务状态与结果。
```json 
{
    "output": {
        "task_status": "PENDING",
        "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx"
    },
    "request_id": "4909100c-7b5a-9f92-bfe5-xxxxxx"
}
```

异常响应
```json
{
    "code":"InvalidApiKey",
    "message":"Invalid API-key provided.",
    "request_id":"fb53c4ec-1c12-4fc4-a580-xxxxxx"
}
```
output object

任务输出信息。

属性

task_id string

任务ID。查询有效期24小时。

task_status string

任务状态。

枚举值

PENDING：任务排队中

RUNNING：任务处理中

SUCCEEDED：任务执行成功

FAILED：任务执行失败

CANCELED：任务已取消

UNKNOWN：任务不存在或状态未知

request_id string

请求唯一标识。可用于请求明细溯源和问题排查。

code string

请求失败的错误码。请求成功时不会返回此参数，详情请参见错误信息。

message string

请求失败的详细信息。请求成功时不会返回此参数，详情请参见错误信息。

步骤2：根据任务ID查询结果
北京地域：GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}

新加坡地域：GET https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}

说明
轮询建议：图像生成过程约需数分钟，建议采用轮询机制，并设置合理的查询间隔（如 10 秒）来获取结果。

任务状态流转：PENDING（排队中）→ RUNNING（处理中）→ SUCCEEDED（成功）/ FAILED（失败）。

结果链接：任务成功后返回图像链接，有效期为 24 小时。建议在获取链接后立即下载并转存至永久存储（如阿里云 OSS）。

QPS 限制：查询接口默认QPS为20。如需更高频查询或事件通知，建议配置异步任务回调。

更多操作：如需批量查询、取消任务等操作，请参见管理异步任务。

请求参数
查询任务结果
请将86ecf553-d340-4e21-xxxxxxxxx替换为真实的task_id。

```shell
curl -X GET https://dashscope.aliyuncs.com/api/v1/tasks/86ecf553-d340-4e21-xxxxxxxxx \
--header "Authorization: Bearer $DASHSCOPE_API_KEY"
```

请求头（Headers）
Authorization string（必选）

请求身份认证。接口使用阿里云百炼API-Key进行身份认证。示例值：Bearer sk-xxxx。

URL路径参数（Path parameters）
task_id string（必选）

任务ID。

响应参数
任务执行成功
图像URL仅保留24小时，超时后会被自动清除，请及时保存生成的图像。
```json 
{
    "request_id": "f767d108-7d50-908b-a6d9-xxxxxx",
    "output": {
        "task_id": "d492bffd-10b5-4169-b639-xxxxxx",
        "task_status": "SUCCEEDED",
        "submit_time": "2025-01-08 16:03:59.840",
        "scheduled_time": "2025-01-08 16:03:59.863",
        "end_time": "2025-01-08 16:04:10.660",
        "results": [
            {
                "orig_prompt": "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵",
                "actual_prompt": "一间有着精致雕花窗户的花店，漂亮的深色木质门上挂着铜制把手。店内摆放着各式各样的鲜花，包括玫瑰、百合和向日葵，色彩鲜艳，生机勃勃。背景是温馨的室内场景，透过窗户可以看到街道。高清写实摄影，中景构图。",
                "url": "https://dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com/1.png"
            }
        ],
        "task_metrics": {
            "TOTAL": 1,
            "SUCCEEDED": 1,
            "FAILED": 0
        }
    },
    "usage": {
        "image_count": 1
    }
}
```
任务执行失败
```json
{
    "request_id": "e5d70b02-ebd3-98ce-9fe8-759d7d7b107d",
    "output": {
        "task_id": "86ecf553-d340-4e21-af6e-xxxxxx",
        "task_status": "FAILED",
        "code": "InvalidParameter",
        "message": "xxxxxx",
        "task_metrics": {
            "TOTAL": 4,
            "SUCCEEDED": 0,
            "FAILED": 4
        }
    }
}
```

任务部分失败
```
{
    "request_id": "85eaba38-0185-99d7-8d16-xxxxxx",
    "output": {
        "task_id": "86ecf553-d340-4e21-af6e-xxxxxx",
        "task_status": "SUCCEEDED",
        "results": [
            {
                "url": "https://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/123/a1.png"
            },
            {
                "code": "InternalError.Timeout",
                "message": "An internal timeout error has occurred during execution, please try again later or contact service support."
            }
        ],
        "task_metrics": {
            "TOTAL": 2,
            "SUCCEEDED": 1,
            "FAILED": 1
        }
    },
    "usage": {
        "image_count": 1
    }
}
```

任务查询过期
```
{
    "request_id": "a4de7c32-7057-9f82-8581-xxxxxx",
    "output": {
        "task_id": "502a00b1-19d9-4839-a82f-xxxxxx",
        "task_status": "UNKNOWN"
    }
}
```

output object

任务输出信息。

属性

task_id string

任务ID。查询有效期24小时。

task_status string

任务状态。

枚举值

PENDING：任务排队中

RUNNING：任务处理中

SUCCEEDED：任务执行成功

FAILED：任务执行失败

CANCELED：任务已取消

UNKNOWN：任务不存在或状态未知

轮询过程中的状态流转：

PENDING（排队中） → RUNNING（处理中）→ SUCCEEDED（成功）/ FAILED（失败）。

初次查询状态通常为 PENDING（排队中）或 RUNNING（处理中）。

当状态变为 SUCCEEDED 时，响应中将包含生成的图像url。

若状态为 FAILED，请检查错误信息并重试。

submit_time string

任务提交时间。格式为 YYYY-MM-DD HH:mm:ss.SSS。

scheduled_time string

任务执行时间。格式为 YYYY-MM-DD HH:mm:ss.SSS。

end_time string

任务完成时间。格式为 YYYY-MM-DD HH:mm:ss.SSS。

results array of object

任务结果列表，包括图像URL、prompt、部分任务执行失败报错信息等。

数据结构

属性

orig_prompt string

原始输入的prompt，对应请求参数prompt。

actual_prompt string

开启 prompt 智能改写后，返回实际使用的优化后 prompt。若未开启该功能，则不返回此字段。

url string

图像URL地址。仅在 task_status 为 SUCCEEDED 时返回。链接有效期24小时，可通过此URL下载图像。

code string

请求失败的错误码。请求成功时不会返回此参数，详情请参见错误信息。

message string

请求失败的详细信息。请求成功时不会返回此参数，详情请参见错误信息。

task_metrics object

任务结果统计。

属性

TOTAL integer

总的任务数。

SUCCEEDED integer

任务状态为成功的任务数。

FAILED integer

任务状态为失败的任务数。

code string

请求失败的错误码。请求成功时不会返回此参数，详情请参见错误信息。

message string

请求失败的详细信息。请求成功时不会返回此参数，详情请参见错误信息。

usage object

输出信息统计。只对成功的结果计数。

属性

image_count integer

模型成功生成图片的数量。计费公式：费用 = 图片数量 × 单价。

request_id string

请求唯一标识。可用于请求明细溯源和问题排查。

DashScope SDK调用
SDK 的参数命名与HTTP接口基本一致，参数结构根据语言特性进行封装。

由于文生图任务耗时较长（通常为1-2分钟），SDK 在底层封装了 HTTP 异步调用流程，支持同步、异步两种调用方式。

具体耗时受限于排队任务数和服务执行情况，请在获取结果时耐心等待。
Python SDK调用
说明
推荐安装最新版DashScope Python SDK，否则可能运行报错：安装或升级SDK。

同步调用
请求示例
```python
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
import os
import dashscope

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
# 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
api_key = os.getenv("DASHSCOPE_API_KEY")

print('----sync call, please wait a moment----')
rsp = ImageSynthesis.call(api_key=api_key,
                          model="wan2.5-t2i-preview",
                          prompt="一间有着精致窗户的花店，漂亮的木质门，摆放着花朵",
                          negative_prompt="",
                          n=1,
                          size='1024*1024',
                          prompt_extend=True,
                          watermark=False,
                          seed=12345)
print('response: %s' % rsp)
if rsp.status_code == HTTPStatus.OK:
    # 在当前目录下保存图片
    for result in rsp.output.results:
        file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
        with open('./%s' % file_name, 'wb+') as f:
            f.write(requests.get(result.url).content)
else:
    print('sync_call Failed, status_code: %s, code: %s, message: %s' %
          (rsp.status_code, rsp.code, rsp.message))
响应示例
url 有效期24小时，请及时下载图像。
 
{
    "status_code": 200,
    "request_id": "9d634fda-5fe9-9968-a908-xxxxxx",
    "code": null,
    "message": "",
    "output": {
        "task_id": "d35658e4-483f-453b-b8dc-xxxxxx",
        "task_status": "SUCCEEDED",
        "results": [{
            "url": "https://dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com/1.png",
            "orig_prompt": "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵",
            "actual_prompt": "一间精致的花店，窗户上装饰着优雅的雕花，漂亮的木质门上挂着铜制把手。店内摆放着各种色彩鲜艳的花朵，如玫瑰、郁金香和百合等。背景是温馨的室内场景，光线柔和，营造出宁静舒适的氛围。高清写实摄影，近景中心构图。"
        }],
        "submit_time": "2025-01-08 19:36:01.521",
        "scheduled_time": "2025-01-08 19:36:01.542",
        "end_time": "2025-01-08 19:36:13.270",
        "task_metrics": {
            "TOTAL": 1,
            "SUCCEEDED": 1,
            "FAILED": 0
        }
    },
    "usage": {
        "image_count": 1
    }
}
```
响应示例
url 有效期24小时，请及时下载图像。
```json
{
    "request_id": "22f9c744-206c-9a78-899a-xxxxxx",
    "output": {
        "task_id": "4a0f8fc6-03fb-4c44-a13a-xxxxxx",
        "task_status": "SUCCEEDED",
        "results": [{
           "orig_prompt": "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵",
            "actual_prompt": "一间有着精致雕花窗户的花店，漂亮的深色木质门微微敞开。店内摆放着各式各样的鲜花，包括玫瑰、百合和向日葵，色彩鲜艳，香气扑鼻。背景是温馨的室内场景，光线柔和，透过窗户洒在花朵上。高清写实摄影，中景构图。",
            "url": "https://dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com/1.png"
        }],
        "task_metrics": {
            "TOTAL": 1,
            "SUCCEEDED": 1,
            "FAILED": 0
        }
    },
    "usage": {
        "image_count": 1
    }
}
```

使用限制
数据时效：任务task_id和 图像url均只保留 24 小时，过期后将无法查询或下载。

内容审核：输入的 prompt 和输出的图像均会经过内容安全审核，包含违规内容的请求将报错“IPInfringementSuspect”或“DataInspectionFailed”，具体参见错误信息。

网络访问配置：图像链接存储于阿里云 OSS，如果业务系统因安全策略无法访问外部OSS链接，请将以下 OSS 域名加入网络访问白名单。

 
# OSS域名列表
dashscope-result-bj.oss-cn-beijing.aliyuncs.com
dashscope-result-hz.oss-cn-hangzhou.aliyuncs.com
dashscope-result-sh.oss-cn-shanghai.aliyuncs.com
dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com
dashscope-result-zjk.oss-cn-zhangjiakou.aliyuncs.com
dashscope-result-sz.oss-cn-shenzhen.aliyuncs.com
dashscope-result-hy.oss-cn-heyuan.aliyuncs.com
dashscope-result-cd.oss-cn-chengdu.aliyuncs.com
dashscope-result-gz.oss-cn-guangzhou.aliyuncs.com
dashscope-result-wlcb-acdr-1.oss-cn-wulanchabu-acdr-1.aliyuncs.com
计费与限流
模型免费额度和计费单价请参见模型列表与价格。

模型限流请参见通义万相。

计费说明：

按成功生成的 图像张数 计费。仅当查询结果接口返回task_status为SUCCEEDED 并成功生成图像后，才会计费。

模型调用失败或处理错误不产生任何费用，也不消耗免费额度。

文生图还支持节省计划，抵扣顺序为 免费额度 > 节省计划 > 按量付费。

错误码
如果模型调用失败并返回报错信息，请参见错误信息进行解决。