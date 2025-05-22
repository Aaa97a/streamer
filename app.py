from flask import Flask, jsonify
from pytube import YouTube

app = Flask(__name__)

@app.route('/api/v1/video/youtube/<video_id>', methods=["GET"])
def get_video_info(video_id):
    # YouTube の動画 URL を生成
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # pytube を利用して YouTube 動画のオブジェクトを生成
        yt_obj = YouTube(video_url)
        
        # 最高解像度のストリームを取得
        stream = yt_obj.streams.get_highest_resolution()
        
        # 必要なメタ情報を収集
        response = {
            "video_id": video_id,
            "title": yt_obj.title,
            "thumbnail": yt_obj.thumbnail_url,
            "duration": yt_obj.length,   # 単位は秒
            "stream_url": stream.url,
        }
        return jsonify(response)
    except Exception as e:
        # エラー発生時の HTTP 500 エラーとエラーメッセージを返す
        return jsonify({"error": str(e)}), 500

