from flask import Blueprint

main = Blueprint('main', __name__)

from . import video_download, pdf_export, transcribe
