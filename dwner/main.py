from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import zipfile
import yt_dlp
import os
import io
import json

app = Flask(__name__)
BASE_DIR = "/home/lubu/EXT/MP3"

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/dwn")
def dwn():
    songs = {}
    for folder in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, folder)
        if os.path.isdir(path):
            songs[folder] = os.listdir(path)
    return render_template("download_page.html", songs=songs)

@app.route("/link", methods=["POST"])
def link():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        link = data.get("link")
        if link:
            output = download_playlist_audio(link)
            if output:
                return jsonify({'message': 'Download started successfully'}), 200
            else:
                return jsonify({'error': 'Download failed'}), 500
        else:
            return jsonify({'error': 'No link was provided'}), 400
    except Exception as e:
        print(f"Error in link route: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/download/<playlist>/<filename>")
def download_file(playlist, filename):
    folder_path = os.path.join(BASE_DIR, playlist)
    return send_from_directory(folder_path, filename, as_attachment=True)

@app.route("/play/<playlist>/<filename>")
def play_file(playlist, filename):
    folder_path = os.path.join(BASE_DIR, playlist)
    return send_from_directory(folder_path, filename)

@app.route("/download_playlist/<playlist>")
def download_playlist(playlist):
    folder_path = os.path.join(BASE_DIR, playlist)

    # Create an in-memory ZIP archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                # Add each song to the ZIP
                zipf.write(file_path, arcname=filename)

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{playlist}.zip"
    )

def download_playlist_audio(playlist_url):
    os.chdir("/home/lubu/EXT/MP3")
    
    download_info = {
        'current': 0,
        'total': 0,
        'current_filename': ''
    }
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            if 'playlist_index' in d:
                download_info['current'] = d['playlist_index']
                download_info['total'] = d.get('playlist_count', download_info['total'])
                download_info['current_filename'] = d.get('filename', 'Unknown')
                
                print(f"📥 Downloading [{download_info['current']}/{download_info['total']}]: {download_info['current_filename']}")
                
        elif d['status'] == 'finished':
            print(f"✅ Finished [{download_info['current']}/{download_info['total']}]: {d.get('filename', 'Unknown')}")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ignoreerrors': True,
        'quiet': False,
        'nooverwrites': True,
        'progress_hooks': [progress_hook],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        
        print(f"Download completed: {download_info['current']} out of {download_info['total']} files processed")
        return download_info
    except Exception as e:
        print(f"Download error: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)