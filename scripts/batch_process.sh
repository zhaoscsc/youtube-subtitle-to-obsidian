#!/bin/bash
# YouTube频道字幕批量下载并转换
# 优先下载中文字幕

set -e

CHANNEL_URL="$1"
OUTPUT_DIR="$2"
TEMP_DIR="$OUTPUT_DIR/.temp_subs"
PROXY="http://localhost:7890"

if [ -z "$CHANNEL_URL" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "用法: $0 <频道URL> <输出目录> [语言: zh/en]"
    exit 1
fi

mkdir -p "$TEMP_DIR"
mkdir -p "$OUTPUT_DIR"

CHANNEL_NAME=$(echo "$CHANNEL_URL" | sed -E 's/.*@([^/]+).*/\1/')
echo "频道: $CHANNEL_NAME"
echo "输出目录: $OUTPUT_DIR"

echo "获取视频列表..."
VIDEO_LIST=$(yt-dlp --no-update --proxy "$PROXY" --flat-playlist --print "%(title)s|%(url)s|%(id)s" "$CHANNEL_URL" 2>/dev/null)

TOTAL=$(echo "$VIDEO_LIST" | wc -l | tr -d ' ')
echo "视频总数: $TOTAL"

PROCESSED=0
SUCCESS=0
SKIPPED=0
FAILED=0

while IFS='|' read -r TITLE URL ID; do
    PROCESSED=$((PROCESSED + 1))
    
    SAFE_TITLE=$(python3 -c "import unicodedata,re; n=unicodedata.normalize('NFC','$TITLE'); print(re.sub(r'[<>:\"\/\\\\|?*]','_',n)[:100])")
    
    if [ -f "$OUTPUT_DIR/${SAFE_TITLE}.md" ]; then
        echo "[$PROCESSED/$TOTAL] 跳过: $TITLE"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi
    
    echo "[$PROCESSED/$TOTAL] $TITLE"
    
    # 清理临时文件
    rm -f "$TEMP_DIR"/*.vtt 2>/dev/null
    
    # 优先下载中文字幕
    yt-dlp --no-update --proxy "$PROXY" \
        --cookies-from-browser chrome \
        --write-auto-subs --sub-langs "zh-TW,zh-Hans" \
        --convert-subs vtt \
        --skip-download \
        --output "$TEMP_DIR/%(id)s.%(ext)s" \
        "$URL" 2>/dev/null
    
    VTT_FILE=$(ls "$TEMP_DIR"/${ID}*.vtt 2>/dev/null | head -1)
    
    if [ -n "$VTT_FILE" ]; then
        python3 ~/Library/CloudStorage/Dropbox/skill-sync/.agents/skills/youtube-subtitle-to-obsidian/scripts/vtt_to_markdown.py \
            "$VTT_FILE" "$OUTPUT_DIR" "$TITLE" "$CHANNEL_NAME" 2>/dev/null
        rm -f "$VTT_FILE"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "  → 无字幕"
        FAILED=$((FAILED + 1))
    fi
    
    sleep 1
done <<< "$VIDEO_LIST"

echo ""
echo "========== 完成 =========="
echo "成功: $SUCCESS, 跳过: $SKIPPED, 失败: $FAILED"
