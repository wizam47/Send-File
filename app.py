import os
import socket
import qrcode
from io import BytesIO
from flask import Flask, request, send_from_directory, render_template, redirect, url_for, send_file, jsonify  # ← añade jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

LOCAL_IP = get_local_ip()
SERVER_URL = f'http://{LOCAL_IP}:5000'

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files, server_url=SERVER_URL)

@app.route('/qr')
def qr_code():
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=3)
    qr.add_data(SERVER_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró archivo'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre vacío'}), 400
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'ok': True, 'filename': filename})   # ← ahora devuelve JSON

# ── NUEVA: lista de archivos como JSON ────────────────────
@app.route('/files')
def list_files():
    files = sorted(os.listdir(app.config['UPLOAD_FOLDER']))
    return jsonify(files)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# ── NUEVA: eliminar por AJAX ──────────────────────────────
@app.route('/delete/<filename>', methods=['DELETE'])
def delete(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
        return jsonify({'ok': True})
    return jsonify({'error': 'No encontrado'}), 404

if __name__ == '__main__':
    print(f'\n🚀 Servidor corriendo en: {SERVER_URL}')
    app.run(host='0.0.0.0', port=5000, debug=True)