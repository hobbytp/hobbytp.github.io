## Agent Gateway

AgentGateway是istio主要服务提供商solo开发的一个专门针对MCP和A2A协议的网关产品。它由rust开发。
solo agentgateway主要解决的问题是：

1. 把MCP Server包装成传统的API，然后就可以使用传统的API调用方式来调用MCP Server。
2. 支持MCP协议和A2A协议。这个是传统Gateway不能支持的。
3. 提供企业级服务，弥补MCP 协议的不足。

#### Demo： agentgateway docker + mcp/everything server docker

下面的demo演示agentgateway作为mcp-client，everything server作为mcp-server。client和server都是docker容器，使用docker-compose来启动。所有步骤如下，请注意，大部分步骤都需要修改代码。

1. **修改everything的代码**
everything的SSE部分代码已经deprecated了，但是考虑到agentgateway 的streamhandleHttps部分还没有ready。所以暂时还是使用SSE的方式。主要是把SSE在没有client连接的情况下，server端不会主动推送数据。因为当前这个推送逻辑在没有connection的情况下因为没有try...catch...逻辑，所以会失败，并让容器退出。
在修改完代码后，需要重新build image，在servers（mcp的github里面）的目录下，运行下面的命令,注意，最后的"."是当前目录的意思。**这个命令的写法是由Dockerfile里的"COPY src/everything /app"决定的**。

```bash
docker build -f src/everything/Dockerfile -t mcp/everything .
```

2. **在agentgateway的根目录加config.json**

- config.json的格式参考代码目录crates/agentgateway/proto。listener.proto只有一份，target.proto有3份，分别对应不同协议（mcp，a2a，google?）
- mcp/everything里面的sse或streamhandle都用的是3001端口（都是RESTful方式）。stdio方式的mcp server（这里是npx）没有端口，只是agentgateway需要对外暴露以服务端口3000而已。
- targets部分，我添加了“listeners”部分以便和config.jon上面的listeners部分对应起来。
- targets部分的docker-everything是用来连接docker-everything的，注意这里的host是“mcp-server”，这个由docker-compose.yml里面的“Services”配置决定，3001在everything的sse.ts或streamhandleHttps.ts里面的代码hardcode的。

```json
{
    "type": "static",
    "listeners": [
        {
            "name": "sse",
            "protocol": "MCP",
            "sse": {
                "address": "[::]",
                "port": 3000
            }
        },
        {
            "name": "docker-everything",
            "protocol": "MCP",
            "sse": {
                "address": "[::]",
                "port": 3001
            }
        }
    ],
    "targets": {
        "mcp": [
            {
                "name": "everything",
                "listeners": [
                    "sse"
                ],
                "stdio": {
                    "cmd": "npx",
                    "args": [
                        "@modelcontextprotocol/server-everything"
                    ]
                }
            },
            {
                "name": "docker-everything",
                "listeners": [
                    "docker-everything"
                ],
                "sse": {
                    "host": "[::]",
                    "port": 3001,
                    "path": "/sse"
                }
            }
        ]
    }
}

```

3. **agentgateway添加docker-compose.yml**

   - mcp-server下面，command部分是用来覆盖缺省的CMD（是stdio），如果要改成MCP的stream的方式的话，把"start:sse"改成"start:streamableHttps", 另外，这里不需要对外暴露port，因为mcp-client只通过mcp-network连接mcp-server，这个在config.json里面配置。
   - mcp-client下面，volumes使用相对路径，所以要用引号。端口映射部分是为了给外部访问。19000部分，源代码是在127.0.0.1上监听，所以不能对外暴露，我是修改了admin.ts的代码，改成了0.0.0.0. 另外3000和3001都是和config.json里面的listeners部分对应的。

```yaml
services:
  mcp-server:
    image: mcp/everything
    container_name: mcp-server-everything
    command: ["npm", "run", "start:sse"]
    networks:
      - mcp-network

  mcp-client:
    image: ghcr.io/agentgateway/agentgateway:v0.4.24-dirty-ext-mcpsvc
    container_name: agentgateway
    ports:
      - "19000:19000"
      - "3000:3000"
      - "3001:3001"
    volumes:
      - "./config.json:/root/.config/agentgateway/config.json"
    depends_on:
      - mcp-server
    networks:
      - mcp-network

networks:
  mcp-network:
    name: mcp-network
    driver: bridge
```

4. **MCP inspector测试**

   - 运行docker-compose up -d，启动agentgateway和mcp-server。
   - 打开MCP inspector，连接localhost:3000或3001，选择sse协议，点击connect。
   - 在mcp-server的docker容器里面，运行下面的命令，注意这里的"docker-everything"是config.json里面的配置。

```bash
CLIENT_PORT=6274 SERVER_PORT=9000 npx @modelcontextprotocol/inspector
```
