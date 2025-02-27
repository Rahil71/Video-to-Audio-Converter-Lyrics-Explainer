from flask import Flask, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
from moviepy import VideoFileClip
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')

app=Flask(__name__)

UPLOAD_FOLDER='uploads'
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

OUTPUT_FOLDER='converted'
os.makedirs(OUTPUT_FOLDER,exist_ok=True)

@app.route('/home',methods=["POST","GET"])
def home_user():
    return render_template('home.html')
    
@app.route('/lyrics_explain',methods=["POST","GET"])
def explain_lyrics():
    lyrics=request.form.get('lyrics')
    language=request.form.get('language')
    print(f'Lyrics in function: {lyrics}')
    prompt = f"Explain the following song lyrics in {language}:\n\n{lyrics}"
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))
    response = llm.invoke(prompt)
    print(f'Explaination in function:{response.content}')
    user_response=response.content
    return render_template('lyrics.html',lyrics_text=lyrics,lyrics_explaination=user_response)
    
@app.route('/video_to_audio',methods=["POST","GET"])
def video_to_audio():
    file=request.files['video']
    if file and file.filename.endswith('mp4'):
        video_filename=secure_filename(file.filename)
        video_file_path=os.path.join(UPLOAD_FOLDER,video_filename)
        file.save(video_file_path)
    
    audio_filename=video_filename.rsplit('.',1)[0] + '.mp3'
    audio_file_path=os.path.join(OUTPUT_FOLDER,audio_filename)
    audio_file=VideoFileClip(video_file_path)
    audio_file.audio.write_audiofile(audio_file_path)
    audio_file.close()

    os.remove(video_file_path)

    return redirect(url_for('download',filename=audio_filename))

@app.route('/download_file/<filename>')
def download(filename):
    return render_template('download.html',filename=filename)

@app.route('/download/<filename>')
def download_file(filename):
    audio_file_path=os.path.join(OUTPUT_FOLDER,filename)
    return send_file(audio_file_path, as_attachment=True)

if __name__=="__main__":
    app.run(debug=True)