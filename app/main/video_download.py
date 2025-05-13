import traceback

from flask import current_app, request, jsonify
from yt_dlp import YoutubeDL

from app.main import main
from app.utils.parse import filename_reduction


COOKIE_FILE_PATH = '/app/conf/cookies.txt'

def init_yt_downloader(hd=False,
                       audio_only=False,
                       extractor=None) -> YoutubeDL:
    config = current_app.config
    if audio_only:
        ydl_opts = {
            'paths': {
                'home': config.get('DOWNLOAD_DIR'),
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
            if hd and config.get('BILIBILI_COOKIE', None) is not None:
                cookies = config['BILIBILI_COOKIE']
                video_format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            else:
                video_format = 'bv*[height<=480]+ba/b[height<=480] / wv*+ba/w'
        ydl_opts = {
            'paths': {
                'home': config['DOWNLOAD_DIR'],
            },
            'outtmpl': {
                'default': '%(title).10s-%(id)s.%(ext)s',
            },
            'format': video_format,
        }

    if config.get('YOUTUBE_COOKIE', False):
        ydl_opts['cookiefile'] = COOKIE_FILE_PATH

    if config.get('PROXY_MODE', False):
        ydl_opts['proxy'] = config.get('PROXY_URL', 'http://localhost:4000')

    downloader = YoutubeDL(ydl_opts)
    return downloader


@main.route('/videoDownload', methods=['POST'])
def download_video():
    try:
        config = current_app.config
        data = request.get_json()
        print(data)
        url: str = data.get('url')
        download: bool = data.get('download', True)
        hd: bool = data.get('hd', False)
        extractor: str = data.get('extractor')
        audio_only: bool = data.get('audio_only', False)

        downloader = init_yt_downloader(hd=hd, extractor=extractor, audio_only=audio_only)
        with downloader:
            if download:
                downloader.download([url])
            content_info = downloader.extract_info(url, download=False)
            if download:
                file_path = downloader.prepare_filename(content_info)
                # if len(file_path) > 150:
                #     file_path = filename_reduction(file_path)
                file_path_output = file_path if config.get('LOCAL_MODE', True) \
                    else config.get('BASE_URL') + '/fileDownload' + file_path

        return jsonify({
            'message': 'success',
            'content_info': content_info,
            'file_path': file_path_output,
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(
            {'message': 'failed',
             'error': str(e)}), 500