# Change Log

## 2026-03-19 - G03 VoiceCoder v0.2 项目术语提取

- Goal ID: G03-S01
- Summary: 实现术语提取功能，包括语料库扫描、正则匹配标识符、混合权重计算、scan 命令
- Impact: `src/voice_coder/extractor.py`, `tests/test_extractor.py`, 更新 `config.py`、`cli.py`、`recognizer.py`
- Tests: 17/17 passed (config 8 + extractor 9)
- Dead Code: 无
- Security: 无敏感信息泄露
- Commit Status: 待提交

## 2026-03-19 - G02 VoiceCoder v0.1 MVP

- Goal ID: G02-S01
- Summary: 实现核心语音识别功能，包括配置管理、音频采集、Vosk 识别封装、ydotool 键盘输出、CLI 控制器
- Impact: `src/voice_coder/`, `tests/`, `scripts/`, `pyproject.toml`, `README.md`
- Tests: 8/8 passed (config module)
- Dead Code: 无明显死代码
- Security: 无敏感信息泄露
- Commit Status: 待提交

## 2026-03-19 - G01 工作流初始化

- Goal ID: bootstrap
- Summary: Initialized the Claude Code workflow skeleton.
- Impact: `docs/ai`, `.claude/commands`, `.claude/skills`, `.claude/agents`
- Tests: structure verification pending
- Dead Code: not run
- Security: not run
- Commit Status: not committed
