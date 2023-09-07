from flask import Blueprint

main = Blueprint('main', __name__)

from . import download, pdf_export, transcribe
