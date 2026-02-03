import os
import traceback

from flask import current_app, request, jsonify
from yt_dlp import YoutubeDL

from app.main import main

# Get the project root directory (FastFileExporter folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COOKIE_FILE_PATH = os.path.join(PROJECT_ROOT, 'conf', 'cookies.txt')


def get_video_orientation(content_info: dict) -> str:
    if not content_info.get("formats"):
        return 'vertical'
    one_video_info = content_info['formats'][0]
    if one_video_info.get('aspect_ratio', 0.56) < 1:
        return 'vertical' # default as vertical
    return 'horizontal'


def get_format_for_orientation(extractor: str, orientation: str, hd: bool, config) -> str:
    """Return appropriate format string based on video orientation."""
    if extractor == 'youtube':
        if orientation == 'vertical':
            # Vertical video format (e.g., Shorts) - prioritize vertical formats
            return 'bv[ext=mp4]+ba/b'
        else:
            return 'bv[ext=mp4]+(258/256/140)/best' if hd else 'bv*[height<=480]+ba/b[height<=480] / wv*+ba/w'
    elif extractor == 'bilibili':
        if hd and config.get('BILIBILI_COOKIE'):
            return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        return 'bv*[height<=480]+ba/b[height<=480] / wv*+ba/w'
    raise ValueError('no available extractor found')


def init_yt_downloader(hd=False,
                       audio_only=False,
                       extractor=None,
                       no_proxy=False,
                       extract_only=False,
                       video_format=None) -> YoutubeDL:
    config = current_app.config

    # Base options shared across all modes
    base_opts = {
        # 'extractor_args': {'youtube': {'player_client': ['ios', 'web', 'mweb']}},
        'allow_remote_ejs': 'github',
        'allow_remote_components': 'ejs:github',
        'merge_output_format': 'mp4'
    }

    # For extraction only - minimal options, no downloading
    if extract_only:
        ydl_opts = {
            **base_opts,
            'ignore_no_formats_error': True,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'allow_unplayable_formats': True,
        }
    # audio only
    elif audio_only:
        ydl_opts = {
            **base_opts,
            'paths': {
                'home': config.get('DOWNLOAD_DIR'),
            },
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
        }
    # video download
    else:
        # Use provided video_format or determine based on extractor and hd
        if video_format is None:
            if extractor is None:
                raise ValueError('extractor cannot be None')
            elif extractor == 'youtube':
                video_format = 'bv[ext=mp4]+(258/256/140)/best' if hd \
                    else 'bv+ba/b'
            elif extractor == 'bilibili':
                if hd and config.get('BILIBILI_COOKIE', None) is not None:
                    video_format = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    video_format = 'bv*[height<=480]+ba/b[height<=480] / wv*+ba/w'
            else:
                raise ValueError('no available extractor found')

        ydl_opts = {
            **base_opts,
            'paths': {
                'home': config['DOWNLOAD_DIR'],
            },
            'outtmpl': {
                'default': '%(title).10s-%(id)s.%(ext)s',
            },
            'format': video_format,
            'referer': 'https://www.bilibili.com/',
        }

    if config.get('YOUTUBE_COOKIE') and extractor == 'youtube':
        print('Using cookies for youtube')
        ydl_opts['cookiefile'] = COOKIE_FILE_PATH

    if config.get('BILIBILI_COOKIE') and extractor == 'bilibili':
        print('Using cookies for bilibili')
        ydl_opts['cookiefile'] = COOKIE_FILE_PATH

    if config.get('PROXY_MODE', False) and not no_proxy:
        print('Using proxy')
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

        file_path_output = None

        # Phase 1: Extract info only (no downloading)
        with init_yt_downloader(extractor=extractor, extract_only=True) as extractor_dl:
            content_info = extractor_dl.extract_info(url, download=False)

        # Determine video orientation
        orientation = get_video_orientation(content_info)
        print(f'Video orientation: {orientation}')

        # Phase 2: Download with appropriate format based on orientation
        if download:
            if audio_only:
                downloader = init_yt_downloader(audio_only=True, extractor=extractor)
            else:
                video_format = get_format_for_orientation(extractor, orientation, hd, config)
                downloader = init_yt_downloader(extractor=extractor, video_format=video_format)

            with downloader:
                downloader.download([url])
                file_path = downloader.prepare_filename(content_info)
                file_path_output = file_path if config.get('LOCAL_MODE', True) \
                    else config.get('BASE_URL') + '/fileDownload' + file_path

        return jsonify({
            'message': 'success',
            'content_info': content_info,
            'orientation': orientation,
            'file_path': file_path_output,
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify(
            {'message': 'failed',
             'error': str(e)}), 500
