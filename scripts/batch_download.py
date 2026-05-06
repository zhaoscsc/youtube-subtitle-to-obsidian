#!/usr/bin/env python3
"""
YouTube频道字幕批量下载脚本
用法: python batch_download.py <频道URL> <输出目录> [语言: zh/en]
"""

import subprocess
import sys
import json
import re
import os
from pathlib import Path

def get_video_list(channel_url, proxy="http://localhost:7890"):
    """获取频道视频列表"""
    cmd = [
        "yt-dlp", "--flat-playlist", "--print", 
        '{"title":"%(title)s","url":"%(url)s","id":"%(id)s","duration":"%(duration)s"}',
        "--playlist-end", "50",
        channel_url
    ]
    
    env = os.environ.copy()
    env["HTTP_PROXY"] = proxy
    env["HTTPS_PROXY"] = proxy
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    videos = []
    for line in result.stdout.strip().split('\n'):
        if line:
            try:
                videos.append(json.loads(line))
            except:
                pass
    
    return videos

def download_subtitle(video_url, video_id, output_dir, lang="zh", proxy="http://localhost:7890"):
    """下载单个视频字幕"""
    # 字幕语言优先级映射
    lang_map = {
        "zh": ["zh-TW", "zh-Hans", "en-zh-TW"],  # 优先繁中
        "en": ["en-zh-TW", "zh-TW", "zh-Hans"],  # 优先英文
    }
    
    sub_langs = lang_map.get(lang, lang_map["zh"])
    
    temp_dir = output_dir / ".temp_subs"
    temp_dir.mkdir(exist_ok=True)
    
    for sub_lang in sub_langs:
        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--sub-langs", sub_lang,
            "--convert-subs", "vtt",
            "--output", str(temp_dir / "%(id)s.%(ext)s"),
            "--no-playlist",
            "--skip-download",
            video_url
        ]
        
        env = os.environ.copy()
        env["HTTP_PROXY"] = proxy
        env["HTTPS_PROXY"] = proxy
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        # 查找下载的字幕文件
        vtt_file = temp_dir / f"{video_id}.{sub_lang}.vtt"
        if vtt_file.exists():
            return vtt_file
    
    return None

def main():
    if len(sys.argv) < 3:
        print("用法: python batch_download.py <频道URL> <输出目录> [语言: zh/en]")
        sys.exit(1)
    
    channel_url = sys.argv[1]
    output_dir = Path(sys.argv[2])
    lang = sys.argv[3] if len(sys.argv) > 3 else "zh"
    
    print(f"获取视频列表: {channel_url}")
    videos = get_video_list(channel_url)
    print(f"找到 {len(videos)} 个视频")
    
    # 提取频道名
    channel_name = "unknown"
    if "@" in channel_url:
        channel_name = channel_url.split("@")[1].split("/")[0]
    elif "channel/" in channel_url:
        channel_name = channel_url.split("channel/")[1].split("/")[0]
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for i, video in enumerate(videos):
        print(f"\n[{i+1}/{len(videos)}] 处理: {video['title']}")
        
        # 检查是否已存在
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', video['title'])[:100]
        existing_file = output_dir / f"{safe_title}.md"
        if existing_file.exists():
            print(f"  已存在，跳过")
            skip_count += 1
            continue
        
        # 下载字幕
        vtt_file = download_subtitle(
            video['url'], 
            video['id'], 
            output_dir,
            lang
        )
        
        if vtt_file:
            print(f"  字幕下载成功: {vtt_file.name}")
            success_count += 1
        else:
            print(f"  字幕下载失败")
            fail_count += 1
    
    print(f"\n完成! 成功: {success_count}, 失败: {fail_count}, 跳过: {skip_count}")

if __name__ == '__main__':
    main()
