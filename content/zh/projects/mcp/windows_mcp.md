---
title: "每周一个MCP： Windows-MCP"
date: 2025-10-13T15:00:00+08:00
draft: false
tags: ["mcp", "Windows", "Computer Use"]
categories: ["projects"]
description: "Windows-MCP Server 开源项目分析"
wordCount: 1019
readingTime: 3
---


[Windows-MCP](https://github.com/CursorTouch/Windows-MCP) 是一个轻量级的开源项目，旨在实现 AI 代理与 Windows 操作系统的无缝集成，充当 MCP 服务器，能够执行文件导航、应用程序控制、用户界面交互、QA 测试等任务。项目特点包括无需依赖特定 LLM 或视觉技术、丰富的 UI 自动化工具集、实时交互及易扩展性。支持 Windows 7 至 Windows 11，使用 Python 编写并遵循 MIT 许可证。
该MCP是完成“Computer Use”场景中，Windows操作系统的界面控制部分，而Playwright(或Chrome DevTools MCP)是完成“Browser Use”场景中，浏览器的控制部分。


## 工作原理

这个项目通过以下几个核心组件实现Windows界面控制：

### 1. UI自动化库的使用
项目使用 Windows UI Automation API（通过uiautomation库）来发现和操作UI元素，同时结合 PyAutoGUI 库来执行鼠标和键盘操作

Windows UI Automation API vs. PyAutoGUI
层次关系：UIA 是“系统级语义接口”，PyAutoGUI 是“用户级输入模拟 + 像素识别”。二者工作层级不同，互不依赖。
互补关系：UIA 提供语义稳定性（控件树、属性、模式），PyAutoGUI 提供通用可见性交互（无语义要求，看到就点）。实践中常组合：语义优先，像素兜底。
平台关系：UIA 仅 Windows；PyAutoGUI 跨平台。Windows 场景下，PyAutoGUI 在底层会调用 Win32 输入合成（如 SendInput），但与 UIA 并无直接调用关系。

### 2. UI元素发现与分类
Tree类 负责遍历UI元素树并将其分类为三种类型:
* 交互式元素（Interactive Elements）：按钮、文本框、复选框、菜单项等可操作控件.
* 信息元素（Informative Elements）：文本、图像等展示信息的控件
* 可滚动元素（Scrollable Elements）：支持水平或垂直滚动的区域
元素的可见性和可用性检查通过遍历算法实现，确保只识别真正可交互的UI元素。

### 3. 桌面状态管理
Desktop类 管理整个桌面环境，主要功能包括：

* 获取桌面状态：捕获当前所有应用程序、UI元素和截图
* 应用程序管理：获取打开的应用列表 、启动应用、切换窗口
* PowerShell命令执行：通过PowerShell执行系统命令

### 4. GUI操作工具
项目提供14个MCP工具来执行各种GUI操作：

4.1 鼠标操作
* Click-Tool：在指定坐标点击UI元素，支持左键/右键/中键和单击/双击/三击
* Drag-Tool：从一个坐标拖拽到另一个坐标
* Move-Tool：移动鼠标到指定位置

4.2 键盘操作
* Type-Tool：在输入框中输入文本，支持清空现有内容
* Shortcut-Tool：执行键盘快捷键组合（如Ctrl+C）
* Key-Tool：按下单个按键

4.3 状态获取
State-Tool：捕获完整的桌面状态，包括所有交互元素、信息元素和可滚动区域

4.4 导航操作
* Scroll-Tool：在指定位置执行滚动操作，支持垂直和水平滚动

4.5 应用管理
* Launch-Tool：从开始菜单启动应用程序
* Switch-Tool：切换到指定的应用窗口并置于前台

### 5. 技术实现细节
* DPI感知：设置进程DPI感知以确保坐标准确
* 并行处理：使用线程池并行遍历多个应用的UI元素树，提高性能
* 元素定位：通过边界框计算随机点来提高点击的可靠性
* 浏览器特殊处理：对浏览器应用有专门的DOM校正逻辑

## Notes
该项目的核心理念是通过 Windows UI Automation API 发现UI元素结构，然后使用 PyAutoGUI 执行实际的鼠标键盘操作。这种组合提供了"视觉可选"的自动化方案——既可以通过UI元素属性进行精确控制，也支持基于截图的视觉识别（当use_vision=True时）。

所有的GUI控制操作都通过FastMCP服务器以MCP工具的形式暴露出来，使得AI助手（如Claude）可以通过这些标准化的工具接口来控制Windows桌面环境。

## 参考
- [Windows-MCP](https://github.com/CursorTouch/Windows-MCP)
- [Windows-Use](https://github.com/CursorTouch/Windows-Use)