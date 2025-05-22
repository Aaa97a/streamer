from flask import Flask, jsonify
from yt_dlp import YoutubeDL
from pytube import YouTube

app = Flask(__name__)

@app.route('/api/v1/video/youtube/<video_id>', methods=["GET"])
def get_video_info(video_id):
    # 対象の YouTube 動画 URL を生成
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # yt-dlp 用のオプション設定（IP ローテーション機能は使用しません）
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
    }

    stream_url = None
    meta_info = {}

    # --- 1. yt-dlp による動画情報取得 ---
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            meta_info = {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration')
            }
    except Exception as e:
        app.logger.error(f"yt-dlp による取得エラー: {e}")

    # --- 2. yt-dlp で取得できなかった場合は pytube にフォールバック ---
    if not stream_url:
        try:
            yt_obj = YouTube(video_url)
            stream = yt_obj.streams.get_highest_resolution()
            stream_url = stream.url
            meta_info = {
                'title': yt_obj.title,
                'thumbnail': yt_obj.thumbnail_url,
                'duration': yt_obj.length
            }
        except Exception as e:
            return jsonify({
                'error': f'両方の方法で動画情報の取得に失敗しました: {str(e)}'
            }), 500

    response = {
        'video_id': video_id,
        'title': meta_info.get('title'),
        'thumbnail': meta_info.get('thumbnail'),
        'duration': meta_info.get('duration'),
        'stream_url': stream_url
    }

    return jsonify(response)

