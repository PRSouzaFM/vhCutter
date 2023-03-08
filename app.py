from flask import Flask, request, send_file, render_template
import subprocess
import datetime
import os
from werkzeug.utils import secure_filename
import glob 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'

ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi', 'mov', 'mxf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def deleteUploadFiles(path):
    files = glob.glob(path)
    for file in files:
        os.remove(file)

@app.route('/', methods=['GET', 'POST'])
def convert():
    if request.method == "POST":
        deleteUploadFiles('./uploads')
        file = request.files['file']
        start_time = request.form.get('start')
        duration = request.form.get('duration')
        print(start_time, duration)
        # Validate uplodaded file
        if file.filename == '':
            return "No file selected"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            return "File not allowed"
        
        # check if start_time and duration are provided
        if start_time is not None and duration is not None:
            start_time = float(start_time)
            duration = float(duration)
            start_time = str(datetime.timedelta(seconds=start_time))
            duration = str(datetime.timedelta(seconds=duration))
            output_filename = filename.rsplit('.', 1)[0] + '.mp4'
            output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            cmd = f"ffmpeg -i {file_path} -ss {start_time} -t {duration} -c:v libx264 -crf 19 -c:a aac -b:a 192k {output_file_path}"
        else:
            return "start_time and duration are required"
        # run the ffmpeg command
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"
        
        return send_file(output_file_path, mimetype='video/mp4', as_attachment=True)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

