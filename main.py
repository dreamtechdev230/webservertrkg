from flask import Flask, send_from_directory, abort, render_template_string, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
app.secret_key = 'demir423'
REPO_DIR = os.path.abspath("repo")
UPLOAD_PASSWORD = "pisipisi4525"
HIDDEN_FILES = {"shell.php"}
HIDDEN_EXTENSIONS = {".php"}

if not os.path.exists(REPO_DIR):
    os.makedirs(REPO_DIR)

@app.route('/', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def browse(req_path):
    abs_path = os.path.join(REPO_DIR, req_path)
    if not os.path.exists(abs_path):
        return abort(404)
    if os.path.isfile(abs_path):
        filename = os.path.basename(abs_path)
        if filename in HIDDEN_FILES or os.path.splitext(filename)[1] in HIDDEN_EXTENSIONS:
            return abort(403)
        dir_path = os.path.dirname(req_path)
        return send_from_directory(os.path.join(REPO_DIR, dir_path), filename, as_attachment=True)
    files = os.listdir(abs_path)
    files = [f for f in files if f not in HIDDEN_FILES and os.path.splitext(f)[1] not in HIDDEN_EXTENSIONS]
    files.sort()
    entries = []
    if req_path:
        parent_path = os.path.dirname(req_path.rstrip('/'))
        entries.append(f'<li><a href="/{parent_path}">.. (geri)</a></li>')
    for filename in files:
        full_path = os.path.join(req_path, filename)
        is_dir = os.path.isdir(os.path.join(REPO_DIR, full_path))
        icon = "📁" if is_dir else "📄"
        entries.append(f'<li>{icon} <a href="/{full_path}">{filename + "/" if is_dir else filename}</a></li>')
    html = f"""
    <html><head>
    <title>TRKG PACKET MANAGER REPO</title>
    <style>
        body {{ font-family: Tahoma, sans-serif; background: #e0e0e0; padding: 20px; }}
        ul {{ list-style: none; }}
        a {{ text-decoration: none; color: #0000cc; }}
        a:hover {{ text-decoration: underline; }}
    </style>
    </head><body>
    <h2>📁 /{req_path}</h2>
    <ul>{''.join(entries)}</ul>
    <a href="/upload">📤 Yükleme Paneli</a>
    </body></html>
    """
    return render_template_string(html)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        password = request.form.get("password")
        if password != UPLOAD_PASSWORD:
            flash("Şifre yanlış!", "error")
            return redirect(url_for("upload"))
        uploaded_file = request.files.get("file")
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(REPO_DIR, filename))
            flash("Yükleme başarılı!", "success")
            return redirect(url_for("browse"))
    html = """
    <html><head>
    <title>Yükleme Paneli</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #f5f5f5; padding: 30px; }
        .msg { color: red; }
    </style>
    </head><body>
    <h2>Dosya Yükleme Paneli</h2>
    {% with messages = get_flashed_messages(with_categories=True) %}
    {% if messages %}
        <ul>
        {% for category, message in messages %}
        <li class="msg">{{ message }}</li>
        {% endfor %}
        </ul>
    {% endif %}
    {% endwith %}
    <form method="post" enctype="multipart/form-data">
        Şifre: <input type="password" name="password"><br><br>
        Dosya: <input type="file" name="file"><br><br>
        <input type="submit" value="Yükle">
    </form>
    <a href="/">Geri dön</a>
    </body></html>
    """
    return render_template_string(html)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
