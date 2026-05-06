---
name: youtube-subtitle-to-obsidian
description: 批量下载YouTube视频字幕并保存到Obsidian
version: 1.1.0
author: Claude
tags: [youtube, subtitle, obsidian, batch]
---

# YouTube字幕批量获取 → Obsidian

## 功能
- 批量下载YouTube频道视频字幕
- 优先下载**中文字幕**（繁体→简体）
- 合并相邻短句，更易读
- 格式：`**0:00** · 完整字幕内容`

## 脚本位置
```
~/Library/CloudStorage/Dropbox/skill-sync/.agents/skills/youtube-subtitle-to-obsidian/scripts/
```

| 脚本 | 功能 |
|------|------|
| `vtt_to_markdown.py` | VTT转Markdown，合并短句 |
| `batch_process.sh` | 批量下载整个频道 |

## 字幕语言优先级
1. **zh-TW** - 繁体中文
2. **zh-Hans** - 简体中文

## 使用方法

### 批量下载
```bash
~/Library/CloudStorage/Dropbox/skill-sync/.agents/skills/youtube-subtitle-to-obsidian/scripts/batch_process.sh \
  "https://www.youtube.com/@shoshotw/videos" \
  "/Users/zhaoyue/Documents/mywl/1-输入/01-待整理/YouTube"
```

## 输出格式
```markdown
**0:00** · 年假结束了 相信有很多人要展开今年的新年新目标了 可能有的人想减肥 有的人看了我的频道 想开始培养运动习惯

**0:19** · 除了最难的运动习惯以外 美国也有民调公司统计 有49%的受访者在2月底前就已经彻底放弃当初设定的新年目标了
```

## 依赖
- yt-dlp
- Python 3.6+
- Chrome cookies (需登录YouTube)
