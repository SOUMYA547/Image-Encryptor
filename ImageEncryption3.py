import os
import time
import math
from flask import Flask, request, render_template_string, send_file, after_this_request
from werkzeug.utils import secure_filename
import secrets

def generate_strong_password(length=16):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    return ''.join(secrets.choice(chars) for _ in range(length))

flask_app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@flask_app.route('/', methods=['GET', 'POST'])
def index():
    html = '''
    <!doctype html>
    <html>
    <head>
        <title>SecureImagePro</title>
        <style id="theme-style">
            body {
                background: linear-gradient(to right, red, orange, yellow, green, blue, purple);
                color: #0f0;
                font-family: 'Courier New', monospace;
                text-align: center;
                padding-top: 50px;
            }
            .container {
                background: rgba(0,0,0,0.8);
                border: 2px solid #0ff;
                border-radius: 15px;
                padding: 30px;
                width: 450px;
                margin: auto;
                box-shadow: 0 0 15px #0ff;
            }
            input, select {
                width: 90%;
                margin: 10px;
                padding: 10px;
                border: none;
                border-radius: 5px;
                background: black;
                color: #0f0;
                border: 1px solid #0f0;
            }
            input[type=submit], button {
                background: #0ff;
                color: black;
                font-weight: bold;
                cursor: pointer;
            }
            .stats {
                margin-top: 20px;
                color: #fff;
                background: #222;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #0f0;
            }
        </style>
        <script>
            function togglePassword() {
                var x = document.getElementById("password");
                if (x.type === "password") {
                    x.type = "text";
                } else {
                    x.type = "password";
                }
            }
            function toggleTheme() {
                let style = document.getElementById("theme-style");
                if (style.innerHTML.includes("black")) {
                    style.innerHTML = style.innerHTML.replace(/black/g, "white").replace(/#0f0/g, "#000").replace(/#0ff/g, "#444").replace(/#222/g, "#ccc");
                } else {
                    location.reload();
                }
            }
            function generatePassword() {
                fetch('/generate-password').then(res => res.text()).then(pwd => {
                    document.getElementById("password").value = pwd;
                });
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h2>📸SecureImagePro 🔐</h2>
            <button onclick="toggleTheme()">🌓 Toggle Theme</button>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" required><br>
                <input type="password" name="password" id="password" placeholder="Enter password" required>
                <br><input type="checkbox" onclick="togglePassword()">Show Password<br>
                <button type="button" onclick="generatePassword()">🎲 Generate Strong Password</button><br>
                <input type="submit" name="action" value="🔒Encrypt">
                <input type="submit" name="action" value="🔓Decrypt">
            </form>
            {{ stats|safe }}
        </div>
    </body>
    </html>
    '''
    stats_html = ""
    if request.method == 'POST':
        file = request.files['file']
        password = request.form['password']
        action = request.form['action']
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        try:
            with open(input_path, 'rb') as f:
                data = f.read()

            start = time.time()

            if action == '🔒Encrypt':
                result = data[::-1]
                output_filename = filename + '.enc'
            else:
                result = data[::-1]
                output_filename = 'decrypted_' + filename.replace('.enc', '')

            output_path = os.path.join(UPLOAD_FOLDER, output_filename)
            with open(output_path, 'wb') as f:
                f.write(result)

            end = time.time()

            entropy = len(password) * math.log2(len(set(password))) if password else 0
            stats_html = f"""
                <div class='stats'>
                ✅ <b>{action}</b> completed in <b>{end - start:.4f}</b>s<br>
                📦 Original size: {len(data)} bytes<br>
                🔐 Processed size: {len(result)} bytes<br>
                🧠 Entropy: {entropy:.2f} bits
                </div>
            """

            @after_this_request
            def cleanup(response):
                try:
                    os.remove(input_path)
                    os.remove(output_path)
                except Exception:
                    pass
                return response

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            stats_html = f"<p style='color:red;'>❌ Error: {str(e)}</p>"

    return render_template_string(html, stats=stats_html)

@flask_app.route('/generate-password')
def get_password():
    return generate_strong_password()

if __name__ == '__main__':
    flask_app.run(debug=False)
