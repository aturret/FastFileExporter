from flask import current_app, request, jsonify, send_from_directory

from app.main import main

config = current_app.config


@main.route('/fileDownload/<path:filename>', methods=['GET'])
def file_download(filename):
    return send_from_directory(config['DOWNLOAD_DIR'],
                               filename, as_attachment=True)
