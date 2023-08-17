from flask import current_app, request, jsonify


from app.main import main


@main.route('/download', methods=['POST'])
def download():
    url = request.get_json().get('url')
