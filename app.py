from flask import Flask, jsonify
from yt_dlp import YoutubeDL
from pytube import YouTube
import logging

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.DEBUG)

@app.errorhandler(500)
def internal_error(error):
    app.logger.exception(error)
    return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500

@app.route('/api/v1/video/youtube/<video_id>', methods=["GET"])
def get_video_info(video_id):
    # 対象のYouTube動画URLを生成
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    # yt-dlpによる取得のためのオプション設定
    ydl_opts = {
        'quiet': True,           # ログ出力の抑制
        'skip_download': True,   # 動画のダウンロードは行わない
        'format': 'best',        # 利用可能な中で最高品質のストリームを選択
    }
    
    stream_url = None
    meta_info = {}  # タイトル、サムネイル、再生時間などのメタ情報を格納

    # --- 1. yt-dlpでの取得 ---
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
        print("yt-dlp での取得に失敗:", e)
    
    # --- 2. yt-dlpでストリーム URL が取得できなかった場合は、pytubeにフォールバック ---
    if not stream_url:
        try:
            yt_obj = YouTube(video_url)
            stream = yt_obj.streams.get_highest_resolution()
            stream_url = stream.url
            meta_info = {
                'title': yt_obj.title,
                'thumbnail': yt_obj.thumbnail_url,
                'duration': yt_obj.length  # 秒単位での再生時間
            }
        except Exception as e:
            return jsonify({'error': f'両方の方法で動画情報の取得に失敗しました: {str(e)}'}), 500

    # --- 3. 結果の統合とレスポンスの返却 ---
    response = {
        'video_id': video_id,
        'title': meta_info.get('title'),
        'thumbnail': meta_info.get('thumbnail'),
        'duration': meta_info.get('duration'),
        'stream_url': stream_url
    }
    
    return jsonify(response)
