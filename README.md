# YouTube字幕批量获取 → Obsidian

批量下载YouTube频道视频字幕，转换为Obsidian Markdown格式。

## 功能
- 批量下载YouTube频道视频字幕
- 优先下载中文字幕（繁体→简体）
- 合并相邻短句，更易读
- 格式：`**0:00** · 完整字幕内容`

## 输出格式
```markdown
**0:00** · 年假结束了 相信有很多人要展开今年的新年新目标了

**0:19** · 除了最难的运动习惯以外 美国也有民调公司统计
```

## 快速开始

### 依赖
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Python 3.6+
- Chrome cookies (需登录YouTube)

### 使用方法

#### 批量下载
```bash
./scripts/batch_process.sh "https://www.youtube.com/@频道名/videos" "输出目录"
```

#### 单视频
```bash
# 下载字幕
yt-dlp --proxy "http://localhost:7890" --cookies-from-browser chrome \
  --write-auto-subs --sub-langs "zh-TW,zh-Hans" \
  --convert-subs vtt --skip-download \
  --output "%(id)s.%(ext)s" "视频URL"

# 转换
python3 scripts/vtt_to_markdown.py "字幕.vtt" "输出目录" "视频标题" "频道名"
```

## 项目结构
```
youtube-subtitle-to-obsidian/
├── SKILL.md          # Obsidian Skill文档
├── README.md         # 本文件
└── scripts/
    ├── vtt_to_markdown.py   # VTT转Markdown
    └── batch_process.sh       # 批量下载
```

## License
MIT
