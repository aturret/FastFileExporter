import os
import platform
import subprocess
import shlex

from flask import current_app, request, jsonify
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from app.main import main


def convert_html_to_pdf(
    html_string: str, css_string: str, output_filename: str
) -> None:
    font_config = FontConfiguration()
    css_item = CSS(string=css_string, font_config=font_config)
    html_item = HTML(string=html_string)
    pdf_obj = html_item.write_pdf(output_filename, stylesheets=[css_item])


@main.route('/pdfExport', methods=['POST'])
def pdf_export():
    try:
        data = request.get_json()
        html_string = data.get('html_string')
        css_string = data.get('css_string')
        output_filename = data.get('output_filename')
        config = current_app.config
        download_dir = config.get('DOWNLOAD_DIR')
        output_filename = os.path.join(download_dir, output_filename)
        if platform.system() == 'Windows':
            convert_html_to_pdf(
                html_string=html_string,
                css_string=css_string,
                output_filename=output_filename,
            )
        elif platform.system() == 'Linux':
            escaped = shlex.quote(html_string)
            pdf = subprocess.Popen(f"echo {escaped} | weasyprint -e utf-8 - -", shell=True,
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
            'message': 'pdf export failed',
        }), 500
