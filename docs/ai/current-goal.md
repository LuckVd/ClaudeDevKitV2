# Current Goal

## Goal

**G03: VoiceCoder v0.2 - 项目术语提取** ✅ 已完成

实现从项目语料库自动提取热词的功能：
- 扫描指定目录下的代码文件和文档
- 使用正则表达式提取标识符（CamelCase、snake_case、UPPER_SNAKE）
- 基于出现频率和代码角色计算热词权重
- 支持可配置的文件类型扩展

## Current State

**实现完成，测试通过。**

单元测试：17/17 通过

## Completed Work

### 已实现模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 术语提取器 | `src/voice_coder/extractor.py` | 正则匹配、权重计算、热词保存/加载 |
| 配置扩展 | `src/voice_coder/config.py` | 添加 `CorpusConfig`、`hotwords_file` |
| CLI 扩展 | `src/voice_coder/cli.py` | 添加 `scan` 命令 |
| 识别器更新 | `src/voice_coder/recognizer.py` | 支持从热词文件加载 |

### 测试结果

- `tests/test_config.py`: 8 tests passed
- `tests/test_extractor.py`: 9 tests passed

### 功能验证

```
$ voice-coder scan /opt/projects/VoiceCoder -v
扫描目录: /opt/projects/VoiceCoder
文件类型: .py, .js, .ts, .md
输出文件: /root/.config/voice-coder/hotwords.yaml

✓ 扫描完成
  提取术语: 354 个
  输出文件: /root/.config/voice-coder/hotwords.yaml
```

## Acceptance Criteria

- [x] 支持通过 CLI 参数或配置指定语料库路径
- [x] 支持 `.py`, `.js`, `.ts`, `.md` 文件类型
- [x] 支持通过配置扩展其他文件类型
- [x] 正则表达式正确匹配 CamelCase、snake_case、UPPER_SNAKE_CASE
- [x] 权重计算符合混合策略（频率 + 角色）
- [x] 提供 `voice-coder scan <path>` 命令
- [x] scan 命令输出提取的热词数量和权重分布
- [x] 单元测试覆盖术语提取逻辑

## Next Goal

**G04: v0.3 动态更新**

- 文件监控（watchdog）
- 热词热更新
- 防抖机制

## Sync Notes

- v0.2 代码实现完成
- 需要执行 `/ai-sync` 同步到路线图
