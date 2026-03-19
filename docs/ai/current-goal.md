# Current Goal

## Goal

**G04: VoiceCoder v0.3 - 动态更新** ✅ 已完成

实现语料库文件监控和热词动态更新：
- 在 start 命令中集成文件监控
- 使用 watchdog 监控语料库目录
- 文件变化后增量更新热词（仅处理变化的文件）
- 10 秒防抖机制避免频繁更新
- 热词更新后自动重新配置识别器

## Current State

**实现完成，测试通过。**

单元测试：24/24 通过

## Completed Work

### 已实现模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 增量提取器 | `src/voice_coder/extractor.py` | `IncrementalExtractor` 类 |
| 文件监控器 | `src/voice_coder/watcher.py` | `FileWatcher`、`DebouncedUpdater` |
| 识别器扩展 | `src/voice_coder/recognizer.py` | `update_hotwords()` 方法 |
| CLI 扩展 | `src/voice_coder/cli.py` | `--watch`、`--watch-path` 选项 |

### 测试结果

- `tests/test_config.py`: 8 tests passed
- `tests/test_extractor.py`: 9 tests passed
- `tests/test_watcher.py`: 7 tests passed

### 使用方式

```bash
# 启动语音识别并启用文件监控
voice-coder start --watch --watch-path ~/projects/my-project

# 或使用配置文件中的路径
voice-coder start --watch
```

## Acceptance Criteria

- [x] start 命令支持 `--watch` 选项启用文件监控
- [x] 使用 watchdog 监控配置的语料库路径
- [x] 文件变化后延迟 10 秒再更新热词
- [x] 增量更新仅处理变化的文件
- [x] 热词更新后自动重新配置识别器
- [x] 监控日志显示更新状态
- [x] 单元测试覆盖增量更新逻辑

## Next Goal

**G05: v0.4 生产可用**

- CLI 完善（status、config 命令）
- 错误处理优化
- 文档完善

## Sync Notes

- v0.3 代码实现完成
- 需要执行 `/ai-sync` 同步到路线图
