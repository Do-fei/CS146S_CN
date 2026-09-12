# 项目写作 Skills

装在仓库的 `.cursor/skills/`，给 Cursor 本机和云代理一起用。不是装在某台机器的 `~/.cursor/skills/`。

| 目录 | Skill 名 | 用途 | 来源 |
| --- | --- | --- | --- |
| `story-deslop/` | `story-deslop` | 中文网文去 AI 味 | [oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) |
| `humanizer-chinese/` | `humanizer-chinese` | 中文通稿去 AI 味 | [jiji262/humanizer-chinese](https://github.com/jiji262/humanizer-chinese) |
| `antislop/skills/detect-ai-slop/` | `detect-ai-slop` | 只标痕迹、不改写 | [SalZaki/antislop](https://github.com/SalZaki/antislop) |

未装 oh-story 的扫榜、长篇写作，也未装 antislop 的改写 / 打分。`story-deslop` 在 Cursor 里会降级为单独改，不跑它的自定义子代理。

检测脚本：

```bash
python3 .cursor/skills/antislop/shared/slop_count.py --file sfc-vn/docs/设计理念.md
```
