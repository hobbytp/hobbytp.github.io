---
title: "Electron 内存泄露诊断实战指南"
date: 2026-01-11T08:27:40+08:00
tags: ["Electron", "MemoryLeak", "Diagnostic"]
categories: ["technologies"]
description: "Electron 内存泄露诊断实战指南：本文总结了本人在开发ShuTong（一个基于Electron的跨平台桌面应用，通过抓屏来对用户进行认知分析并给出建议以便用户改进的软件）时，对内存泄露的诊断和解决过程。"
wordCount: 2134
readingTime: 6
---

## TL;DR
本文总结了本人在开发ShuTong（一个基于Electron的跨平台桌面应用，通过抓屏来对用户进行认知分析并给出建议以便用户改进的软件）时，对内存泄露的诊断和解决过程。

## 1\. 核心诊断策略：分而治之

Electron 应用由**主进程 (Main Process)** 和 **渲染进程 (Renderer Process)** 组成。诊断的第一步是确定泄露发生的源头。

### **步骤 1.1：宏观观察与进程识别**

使用 Electron 自带的 API 或系统工具来区分是哪个进程在膨胀。Electron 在任务管理器中会显示多个进程，**准确识别它们是关键**。

#### **如何读懂任务管理器 (Windows/macOS)**

当你看到任务管理器中有一堆相同的图标时，请关注以下细节：

1. **Windows 用户**：  
   * 在“详细信息”选项卡中，右键点击列标题，选择 **“选择列”**，勾选 **“命令行 (Command Line)”**。这是区分进程的“照妖镜”。  
   * **主进程 (Main)**：通常没有 \--type= 参数，或者看起来是最短的那行启动命令。**如果这就是占用最高的进程，请直接跳转到第 3 章。**  
   * **渲染进程 (Renderer)**：包含 \--type=renderer 参数。每一个打开的窗口或 BrowserView 通常对应一个。  
   * **GPU 进程**：包含 \--type=gpu-process 参数。显存泄露（如 WebGL 未释放）看这里。  
   * **工具进程**：包含 \--type=utility（如 Network Service）。  
2. **macOS 用户**：  
   * 打开“活动监视器”。  
   * 通常会明确标记为 Electron Helper (Renderer)、Electron Helper (GPU)。

### **步骤 1.2：锁定目标 PID**

* **方法**：启动应用，进行重复操作（如打开/关闭窗口，路由跳转），观察哪一个 PID 的内存持续增长且在 GC（垃圾回收）后不回落。  
* **技巧**：在 Electron 应用内（控制台）输入 process.pid 可以获得主进程 ID；在开发者工具控制台输入 process.pid 可以获得当前渲染窗口的 ID。将这些 ID 与任务管理器对照。

## **2\. 渲染进程 (Renderer Process) 诊断方案**

渲染进程的泄露通常与前端框架（React/Vue）、未清理的 DOM 引用或闭包有关。

### **方案 A：Chrome DevTools Heap Snapshot (堆快照) 对比法**

这是最精确的定位方法。

**执行步骤：**

1. 打开 DevTools \-\> **Memory** 面板。  
2. **基准快照**：应用启动并稳定后，点击垃圾回收图标（垃圾桶），然后拍第一个快照 (Snapshot 1)。  
3. **操作复现**：执行怀疑导致泄露的操作（例如：打开一个弹窗然后关闭它）。  
4. **回归操作**：尝试回到基准状态。  
5. **目标快照**：再次点击垃圾回收图标，拍第二个快照 (Snapshot 2)。  
6. **对比分析**：  
   * 在 Memory 面板中选择 Snapshot 2。  
   * 将视图从 "Summary" 切换为 **"Comparison"**。  
   * 选择对比目标为 Snapshot 1。  
   * 按 **Delta**（差值）排序。

**寻找目标：**

* **Detached DOM Trees (分离的 DOM 树)**：这是 Electron 中最常见的泄露。意味着 DOM 元素已从页面移除，但 JavaScript 中仍有引用（如未注销的事件监听器）。  
* **Internal Node / JS Objects**：如果大量特定对象（如 BigDataComponent）数量为正增长，说明组件未销毁。

### **方案 B：Allocation Timeline (分配时间轴)**

如果泄露是动态发生的（例如滚动时内存飙升），使用此工具。

1. 选择 **Allocation instrumentation on timeline**。  
2. 点击录制，开始执行操作。  
3. 观察蓝色柱状条（分配）和灰色柱状条（释放）。  
4. 如果操作结束并强制 GC 后，仍有大量蓝色柱状条未变灰，该时间段分配的对象即为泄露源。

## **3\. 主进程 (Main Process) 诊断方案**

如果确定是主进程（没有 \--type 参数的那个）内存占用过高，请按以下步骤操作。

### **3.1 常见嫌疑人清单 (Checklist)**

主进程泄露通常比渲染进程更隐蔽，常见原因如下：

* **堆外内存 (Off-Heap / Native)**：这是 Electron 最隐蔽的杀手。JS 堆快照很小，但总内存巨大。通常由 nativeImage、Buffer 或 C++ 插件引起。  
* **僵尸窗口 (Zombie Windows)**：窗口关闭了，但 JavaScript 变量（如数组或对象）里还存着 BrowserWindow 的引用。  
* **无限增长的缓存**：在 global 变量或模块级变量中存储数据（如日志数组），但没有设置长度限制。

### **3.2 方案 A：远程调试 (Remote Debugging)**

主进程本质是 Node.js 进程，可以复用 Chrome 的调试工具。

**执行步骤：**

1. 启动 Electron 时添加检查标志：  
   electron \--inspect=5858 .
   因为我用的是Vite来做开发部署，所以这个需要在vite.config.ts中配置,如下：
   ```typescript
       electron({
      main: {
        // Shortcut of `build.lib.entry`.
        entry: 'electron/main.ts',
        onstart(args) {
          // Enable remote debugging
          args.startup(['.', '--inspect=5858'])
        },
        ...
      }
    })
   ```

2. 在 Chrome 浏览器访问 chrome://inspect。  
3. 点击 "Configure"，添加 localhost:5858。  
4. 在 "Remote Target" 中找到你的应用主进程，点击 "inspect"。  
5. 此时你拥有了针对主进程的 Memory 面板。
**注意**：我在这里发现JS的Heap其实很小（~40M），但是RSS却很大（~5G），所以内存问题不在这里。

### **3.3 方案 B：编程方式监控 (Programmatic Monitoring) \- 升级版**

此脚本专门用于区分 **JS 堆泄露** 和 **堆外内存泄露**。

// 在 main.js 中  
setInterval(() \=\> {  
  const used \= process.memoryUsage();  
  const allWindows \= require('electron').BrowserWindow.getAllWindows();  
    
  // 计算堆外内存：RSS (物理总内存) \- HeapTotal (V8 申请的堆内存)  
  const offHeapMemory \= used.rss \- used.heapTotal;  
    
  console.log(\`  
  \[Memory Monitor\]  
  Time: ${new Date().toLocaleTimeString()}  
  Process ID: ${process.pid}  
  Active Windows: ${allWindows.length}   
  \--------------------------------------------------  
  RSS (Total):      ${(used.rss / 1024 / 1024).toFixed(2)} MB  
  Heap Used (JS):   ${(used.heapUsed / 1024 / 1024).toFixed(2)} MB  
  Off-Heap (Native): ${(offHeapMemory / 1024 / 1024).toFixed(2)} MB  \<-- 重点关注  
  External (Buffer): ${(used.external / 1024 / 1024).toFixed(2)} MB  
  \--------------------------------------------------  
  \`);  
}, 5000);

**关键诊断逻辑：**

* **场景 1：JS 泄露**  
  * Heap Used 持续增长。  
  * **原因**：全局变量、闭包、未清理的事件监听器。  
  * **对策**：看 Heap Snapshot 中的 Retainers。  
* **场景 2：堆外泄露 (Off-Heap Leak)**  
  * Heap Used 很小且稳定（例如 40MB），但 RSS 巨大（例如 5GB）且 Off-Heap 持续增长。  
  * **原因**：nativeImage (Electron 图片)、Buffer (文件流/视频流)、C++ 原生模块。  
  * **对策**：重点排查 desktopCapturer 和图片处理逻辑。

### **3.4 方案 C：在 Snapshot 中寻找“隐形”内存**

如果确认是堆外泄露，在 Heap Snapshot 中不要只看 Constructor，请尝试：

1. **搜索 ArrayBuffer 或 Uint8Array**：查看 Retained Size 是否异常大。这通常对应 Node.js 的 Buffer 数据。  
2. **搜索 native\_bind 或 WeakRef**：这些通常是 JS 对象持有 C++ 资源的句柄。虽然句柄本身很小，但它对应的底层资源可能巨大。

## **4\. Electron 特有的泄露陷阱 (Checklist)**

在通过工具定位到大致方向后，对照此清单排查代码：

### **4.1 屏幕录制与 desktopCapturer (高危)**

这是 Electron 应用中内存爆炸的头号嫌疑人。

* **问题**：desktopCapturer.getSources 会为每个窗口/屏幕生成缩略图。这些缩略图存储在原生内存中。如果请求了高分辨率缩略图且未释放，内存会瞬间激增。  
* **修复**：  
  1. 仅在需要时请求 thumbnailSize。  
  2. 获取完需要的资源 ID 后，尽快将不需要的 sources 数组置空。  
  3. **重要技巧**：如果只需要 ID 不需要图，设置 thumbnailSize: { width: 0, height: 0 }。

// 优化前：可能导致大量 nativeImage 驻留内存  
// const sources \= await desktopCapturer.getSources({ types: \['window', 'screen'\] });

// 优化后：不获取缩略图，或者用完即弃  
const sources \= await desktopCapturer.getSources({   
  types: \['window', 'screen'\],  
  thumbnailSize: { width: 0, height: 0 } // 关键！不生成预览图  
});

### **4.1.2 进阶实战：WGC 崩溃与跨平台混合策略**

* 场景：Windows (双显卡环境) 下 desktopCapturer 导致内存 OOM 或崩溃；macOS 下正常。
* 策略：条件性 Bypass。只在 Windows 使用 node-screenshots (DXGI)，macOS 继续使用 Electron 原生 API (ScreenCaptureKit) 以确保权限兼容性。
```javascript
// capture-factory.js
const { desktopCapturer } = require('electron');
const os = require('os');

async function captureScreen() {
  // ✅ 针对 Windows 的特殊处理 (DXGI Bypass)
  if (process.platform === 'win32') {
    try {
      const { Monitor } = require("node-screenshots");  //DXGI
      const monitor = Monitor.fromPoint(0, 0); // 获取主屏幕
      const image = await monitor.captureImage();
      return await image.toPng(); // 返回 Buffer
    } catch (e) {
      console.error("Native screenshot failed, falling back to Electron", e);
      // 可以在这里做降级处理
    }
  }

  // ✅ macOS / Linux 使用官方 API (更稳定，权限管理更好)
  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: { width: 1920, height: 1080 }
  });
  return sources[0].thumbnail.toPNG();
}


```


### **4.2 IPC 通信泄露**

* **现象**：每次操作都会注册新的 IPC 监听器。  
* **错误代码**：ipcRenderer.on 没有对应的 removeListener。  
* **修复**：使用 ipcRenderer.invoke (单次请求-响应模式) 代替 on/send 模式。

### **4.3 Node.js Buffer 问题**

* **Node.js Buffer**：Buffer.allocUnsafe 分配的内存属于堆外内存。如果你引用了 Buffer 的一小部分（Slice），整个 Buffer 内存块都不会被回收。  
* **修复**：如果只需要 Buffer 的一小部分，请使用 Buffer.from(buf.slice(...)) 复制一份数据，断开与原大内存块的引用。

### **4.4 remote 模块 (遗留项目)**

* **风险**：remote 模块会让渲染进程直接持有主进程对象的引用。  
* **建议**：完全移除 remote 模块，改用 contextBridge。

## **5\. 自动化泄露检测 (Executable Plan)**

为了防止泄露回归，建议建立自动化测试。

**工具**：spectron (已过时) 或 **playwright** (推荐) \+ electron。

**Playwright 测试脚本示例：**
```javascript
const { _electron: electron } = require('playwright');
const { test, expect } = require('@playwright/test');

test('memory usage should be stable after opening/closing windows', async () => {
  const app = await electron.launch({ args: ['main.js'] });
  const window = await app.firstWindow();

  // 1. 获取基准内存
  const getMemory = async () => await app.evaluate(() => process.memoryUsage().heapUsed);
    
  // 强制 GC (需要启动时开启 --js-flags="--expose-gc")
  await app.evaluate(() => { if (global.gc) global.gc(); });
  const initialMemory = await getMemory();

  // 2. 压力测试：循环执行操作 50 次
  for (let i = 0; i < 50; i++) {
    await window.click('#open-dialog-btn');
    await window.click('#close-dialog-btn');
  }

  // 3. 再次强制 GC
  await app.evaluate(() => { if (global.gc) global.gc(); });
  const finalMemory = await getMemory();

  // 4. 断言：允许一定的浮动，但不能呈线性增长
  expect(finalMemory - initialMemory).toBeLessThan(10 * 1024 * 1024);

  await app.close();
});
```
## **6\. 总结与行动路线**

1. **复现**：确定是主进程还是渲染进程泄露。  
2. **定位**：  
   * 如果 **Heap 正常但 RSS 极高** \-\> 查 desktopCapturer、nativeImage、Buffer。  
   * 如果 **Heap 持续增长** \-\> 查 JS 闭包、全局变量、Detached DOM。  
3. **修复**：优化图片处理，清理 IPC 监听器。  
4. **预防**：引入集成测试监控内存增长趋势。