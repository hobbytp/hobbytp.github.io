# 完善博客数字分身助手 (Digital Twin Chatbot)

## 目标
完成基于 RAG 的博客数字分身助手功能，修复 CSS 加载问题，引入必要的 JS 依赖，并优化提示词以支持中文回复。

## 变更内容

### 1. 修复样式加载
- **操作**: 将 `assets/css/chat.css` 移动到 `assets/css/extended/chat.css`。
- **原因**: Hugo PaperMod 主题的 CSS 打包逻辑（在 `head.html` 中）只会自动加载 `assets/css/extended/` 目录下的扩展样式文件。当前文件位于 `assets/css/` 根目录，因此未被加载，导致聊天窗口无样式。

### 2. 引入 Marked.js 依赖
- **操作**: 在 `layouts/partials/chatbox.html` 顶部添加 Marked.js 的 CDN 引用。
  ```html
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  ```
- **原因**: 前端代码依赖 `marked` 库来渲染 AI 返回的 Markdown 格式回复。目前该库未被引入，导致 Markdown 渲染功能失效。

### 3. 优化后端提示词 (System Prompt)
- **操作**: 修改 `functions/api/chat.js` 中的 `buildSystemPrompt` 函数。
- **变更点**:
  - 将 System Prompt 的指令语言调整为更自然的中文设定。
  - 明确指定“找不到内容”时的回复语为用户要求的：“没有找到相关内容”。
  - 确保 AI 默认使用中文回答。

## 验证计划
1.  **样式验证**: 部署后检查右下角是否出现悬浮聊天按钮，点击是否能正常展开聊天窗口。
2.  **功能验证**: 发送测试消息（如“你好”），确认是否收到回复。
3.  **Markdown 验证**: 询问需要代码块或列表回复的问题，确认渲染是否正常。
4.  **RAG 验证**: 询问博客相关问题，确认回复基于上下文。
5.  **Fallback 验证**: 询问无关问题（如“番茄炒蛋怎么做”），确认回复“没有找到相关内容”。
