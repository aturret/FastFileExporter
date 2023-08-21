import traceback

from flask import current_app, request, jsonify
from yt_dlp import YoutubeDL

from app.main import main


def init_yt_downloader(url,
                       hd=False,
                       audio_only=False,
                       extractor=None) -> YoutubeDL:
    config = current_app.config
    if audio_only:
        ydl_opts = {
            'paths': {
                'home': config['DOWNLOAD_DIR'],
            },
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        }
    else:
        if extractor is None:
            raise ValueError('extractor cannot be None')
        elif extractor == 'youtube':
            video_format = 'bestvideo[ext=mp4]+(258/256/140)/best' if hd \
                else 'bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4]/ wv*+ba[ext=m4a]/w'
        elif extractor == 'bilibili':
            if hd and config['BILIBILI_COOKIE'] is not None:
                cookies = config['BILIBILI_COOKIE']
                video_format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                video_format = 'bv*[height<=480]+ba/b[height<=480] / wv*+ba/w'
        ydl_opts = {
            'paths': {
                'home': config['DOWNLOAD_DIR'],
            },
            'outtmpl': {
                'default': '%(title)s-%(id)s.%(ext)s',
            },
            'format': video_format,
        }
    downloader = YoutubeDL(ydl_opts)
    return downloader


@main.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        print(data)
        url: str = data.get('url')
        download: bool = data.get('download', True)
        hd: bool = data.get('hd', False)
        extractor: str = data.get('extractor')
        audio_only: bool = data.get('audio_only', False)

        downloader = init_yt_downloader(url=url, hd=hd, extractor=extractor, audio_only=audio_only)
        with downloader:
            if download:
                downloader.download([url])
            content_info = downloader.extract_info(url, download=False)
            file_path = downloader.prepare_filename(content_info) if download else None
        return jsonify({
            'message': 'success',
            'content_info': content_info,
            'file_path': file_path,
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(
            {'message': 'failed',
             'error': str(e)}), 500
