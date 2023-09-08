import os
import platform
import subprocess
import shlex
import traceback
from pathlib import Path

from flask import current_app, request, jsonify
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from app.main import main


def convert_html_to_pdf(
    output_filename: str, html_string: str = None, html_file: str = None
) -> None:
    try:
        font_config = FontConfiguration()
        css_item = CSS(filename="pdf_export.css", font_config=font_config)
        if html_file:
            html_item = HTML(filename=html_file, encoding="utf-8")
        elif html_string:
            html_item = HTML(string=html_string)
        html_item.write_pdf(output_filename, stylesheets=[css_item])
    except Exception as e:
        traceback.print_exc()
        raise e


@main.route('/pdfExport', methods=['POST'])
def pdf_export():
    try:
        data = request.get_json()
        print(f"data: {data}")
        method = data.get('method')
        html_string = data.get('html_string', None)
        html_file = data.get('html_file', None)
        config = current_app.config
        download_dir = config.get('DOWNLOAD_DIR')
        output_filename = data.get('output_filename')
        output_filename = os.path.join(download_dir, output_filename)
        print(f"output_filename: {output_filename}")
        if platform.system() == 'Windows':
            print("Windows")
            convert_html_to_pdf(
                html_string=html_string,
                html_file=html_file,
                output_filename=output_filename,
            )
        elif platform.system() == 'Linux' and method == 'file':
            print("Linux")
            html_file_path = str(Path(html_file))
            pdf = subprocess.Popen(f"weasyprint -s pdf_export.css -e utf-8 \"{html_file_path}\" -", shell=True,
                                   stdout=subprocess.PIPE).stdout.read()
            file_output = open(output_filename, 'wb')
            file_output.write(pdf)
            file_output.close()
        return jsonify({
            'status': 'success',
            'message': 'pdf export success',
            'output_filename': output_filename,
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'failed',
            'message': f'pdf export failed{str(e)}',
        }), 500
