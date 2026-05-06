#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VTT字幕转Obsidian Markdown
合并相邻短句，格式：**0:00** · 完整句子
"""

import re
import sys
import os
from datetime import datetime
from pathlib import Path
import unicodedata

def safe_filename(name):
    name = unicodedata.normalize('NFC', name)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name

def parse_vtt(vtt_path):
    """解析VTT文件，合并相邻短句"""
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r'^WEBVTT.*?\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^Kind:.*?\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'^Language:.*?\n', '', content, flags=re.MULTILINE)
    
    pattern = r'(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*\n(.*?)(?=\n\n\d{2}:|\n\d{2}:|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    segments = []
    for match in matches:
        start_m = int(match[1])
        start_s = int(match[2])
        start_ms = int(match[3])
        
        # 时间戳（分:秒）
        ts = f"{start_m}:{start_s:02d}"
        
        # 清理文本
        text = match[8].strip()
        text = re.sub(r'\s+', ' ', text)
        
        if text:
            segments.append({
                'start': ts,
                'start_m': start_m,
                'start_s': start_s,
                'text': text
            })
    
    # 合并相邻短句（同一分钟内或时间差<15秒的合并）
    merged = []
    if segments:
        current = segments[0].copy()
        
        for seg in segments[1:]:
            # 计算时间差
            diff = (seg['start_m'] - current['start_m']) * 60 + (seg['start_s'] - current['start_s'])
            
            # 如果时间差<15秒且在同一分钟附近，合并
            if diff < 15 and seg['start_m'] == current['start_m']:
                current['text'] += ' ' + seg['text']
            else:
                merged.append(current)
                current = seg.copy()
        
        merged.append(current)
    
    return merged

def generate_markdown(video_id, video_title, channel, segments, source_url):
    now = datetime.now().strftime('%Y-%m-%d')
    
    if segments:
        last_ts = segments[-1]['start']
        duration = last_ts
    else:
        duration = "0:00"
    
    frontmatter = f"""---
aliases: []
tags: [youtube, 字幕, {channel}]
创建时间: {now}
修改时间: {now}
source_url: {source_url}
video_id: {video_id}
video_title: "{video_title}"
channel: {channel}
duration: {duration}
---

"""
    
    body = ""
    for seg in segments:
        body += f"**{seg['start']}** · {seg['text']}\n\n"
    
    return frontmatter + body

def main():
    if len(sys.argv) < 2:
        print("用法: python vtt_to_markdown.py <vtt文件> [输出目录] [视频标题] [频道名]")
        sys.exit(1)
    
    vtt_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    video_title = sys.argv[3] if len(sys.argv) > 3 else vtt_path.stem
    channel = sys.argv[4] if len(sys.argv) > 4 else "unknown"
    
    video_id = vtt_path.stem.split('.')[0]
    source_url = f"https://www.youtube.com/watch?v={video_id}"
    
    safe_title = safe_filename(video_title)
    segments = parse_vtt(vtt_path)
    
    if not segments:
        print(f"警告: 未能从 {vtt_path} 解析到字幕")
        segments = []
    
    markdown = generate_markdown(video_id, video_title, channel, segments, source_url)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{safe_title}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"已生成: {output_file}")
    print(f"字幕段数: {len(segments)}")

if __name__ == '__main__':
    main()
