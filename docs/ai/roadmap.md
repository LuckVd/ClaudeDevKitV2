# 项目路线图

本文件是项目总体技术设计与长期进度的唯一事实来源。

使用原则：

- 总体技术方向、阶段规划、目标拆分、依赖关系统一写在这里。
- 当前正在执行的目标细节写在 `current-goal.md`，不要把步骤级执行过程堆到本文件。
- 路线图中的目标和子目标必须使用稳定编号，便于依赖跟踪和同步。
- 目标完成后的实现结果、测试结果、提交记录应回写到本文件表格中。

## 1. 项目概述

- 项目名称：VoiceCoder
- 技术目标：项目感知型语音输入工具，能够识别项目专属术语并自动学习新词
- 当前阶段：v0.2 项目术语提取完成，进入 v0.3 规划
- 主文档说明：本文件负责记录总体设计、阶段目标和实现进度。

## 2. 总体技术架构

### 2.1 核心模块

| 模块ID | 模块名称 | 职责 | 关键接口/输入输出 | 备注 |
|---|---|---|---|---|
| M01 | config | 配置管理 | `load_config(path) -> Config` | YAML 配置加载 |
| M02 | audio | 音频采集 | `AudioCapture.read() -> bytes` | PyAudio 封装 |
| M03 | recognizer | 语音识别 | `Recognizer.process(bytes) -> str` | Vosk 封装 |
| M04 | emitter | 键盘输出 | `KeyboardEmitter.type_text(str)` | ydotool 封装 |
| M05 | cli | 命令行接口 | `voice-coder start/stop/scan` | click 框架 |
| M06 | extractor | 术语提取 | `TermExtractor.scan() -> ExtractionResult` | 正则匹配 + 权重计算 |

### 2.2 关键集成关系

- 用户语音 → AudioCapture → Recognizer → KeyboardEmitter → 当前焦点窗口
- 外部依赖：Vosk 模型、ydotool、PortAudio

## 3. 设计约束

- 优先复用现有模块，不要为单个目标创建孤立实现。
- 敏感信息不得硬编码在源码、配置或容器文件中。
- 当前目标实现应遵循 TDD，至少保证目标相关测试通过。
- 仅支持 Linux 桌面环境（PulseAudio/PipeWire）。
- 仅支持中文语音识别。

## 4. 阶段目标

### G02 VoiceCoder MVP

- 目标名称：VoiceCoder v0.1 MVP
- 目标范围：核心语音识别 + 静态热词 + 键盘模拟
- 完成标准：单元测试通过，CLI 可启动识别循环

## 5. 路线图进度表

填写说明：

- 每一行表示一个目标或子目标。
- 主目标行填写 `目标ID`，`子目标ID` 留空。
- 子目标行同时填写 `目标ID` 和 `子目标ID`。
- `前置依赖` 必须引用已有编号，如 `G01` 或 `G01-S02`。
- `状态` 只能使用以下值：
  - `planned`
  - `designing`
  - `in_progress`
  - `blocked`
  - `done`
  - `dropped`
- `验收结果` 建议使用：
  - `pending`
  - `accepted`
  - `partial`
  - `failed`
- `测试状态` 建议使用：
  - `not_started`
  - `in_progress`
  - `passed`
  - `failed`
- `实现时间` 使用 `YYYY-MM-DD`。
- `Commit ID` 只有在真实提交后才填写；未提交留空。

| 目标ID | 子目标ID | 名称 | 描述 | 状态 | 前置依赖 | 风险/阻塞 | 验收结果 | 测试状态 | 实现时间 | Commit ID | 备注 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G01 |  | 项目基础骨架搭建 | 初始化仓库结构、基础配置和 AI 工作流 | done |  |  | accepted | passed | 2026-03-19 |  | 已完成 |
| G02 |  | VoiceCoder v0.1 MVP | 核心语音识别 + 静态热词 + 键盘模拟 | done | G01 |  | accepted | passed | 2026-03-19 |  | 8 tests passed |
| G02 | G02-S01 | 核心识别模块 | config/audio/recognizer/emitter/cli | done | G01 |  | accepted | passed | 2026-03-19 |  | 所有步骤完成 |
| G03 |  | v0.2 项目术语提取 | 语料库扫描 + 热词生成 | done | G02 |  | accepted | passed | 2026-03-19 |  | 17 tests passed |
| G03 | G03-S01 | 术语提取器 | extractor/cli scan/热词文件加载 | done | G02 |  | accepted | passed | 2026-03-19 |  | 9 tests passed |
| G04 |  | v0.3 动态更新 | 文件监控 + 热词热更新 | planned | G03 |  | pending | not_started |  |  | 下一个目标 |
| G05 |  | v0.4 生产可用 | CLI 完善 + 错误处理 + 文档 | planned | G04 |  | pending | not_started |  |  | 待规划 |

## 6. 开放风险与阻塞

填写说明：

- 这里只记录影响长期推进的风险和阻塞，不记录步骤级实现问题。
- 步骤级问题放在 `current-goal.md` 的 `Blockers` 中。

- 暂无长期风险记录。
