from flask import Flask, request, redirect, render_template, url_for, session, jsonify
from flask_restful import Resource, Api
import os
from functools import wraps
from celery import Celery
from GenerateComic import GenerateComic
import base64 
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI          = os.environ.get('MONGODB_URI') 

app = Flask(__name__)
app.secret_key = 'VeryVeryComify#@666' 

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # Redis broker URL
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'  # Redis result backend

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# API Code
api = Api(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip login for Localhost
        if "127.0.0.1" in request.url_root or "localhost" in request.url_root:
            return f(*args, **kwargs)
        
        if 'google_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@celery.task(bind=True)
def generate_comic_task(self, topic, comic):
    try:
        output_path = f"static/pdfs/{topic[:30].lower().replace(' ', '_').replace('-', '_')}.pdf"
        test = GenerateComic(MONGODB_URI, update_state=self.update_state)
        customisation = comic
        cfg = 9
        step = 25
        generated_images_paths = test.start(topic, customisation, cfg, step, output_path)
        return {"output": "/" + output_path, "img": generated_images_paths}
    except Exception as e:
        return {"error": str(e)}

class Generate(Resource):
    @login_required
    def get(self):
        try:
            topic = request.args.get('topic')  
            comic = request.args.get('comic')  

            # Call the Celery task asynchronously
            result = generate_comic_task.apply_async(args=[topic, comic])
            return {"task_id": result.id}
        except Exception as e:
            return {"error": str(e)}

class TaskStatus(Resource):
    @login_required
    def get(self, task_id):
        try:
            # Query the status of the Celery task using the task ID
            result = generate_comic_task.AsyncResult(task_id)
            status = result.status
            if status == 'PROGRESS':
                response = {
                    'status': status,
                    'progress': result.info.get('progress', 0)
                }
            elif status == 'SUCCESS':
                response = {
                    'status': status,
                    'result': result.result  # If task succeeded, include the result
                }
            else:
                response = {'status': status}
            return jsonify(response)
        except Exception as e:
            return jsonify({'error': str(e)})

# Add resource to API
api.add_resource(Generate, '/generate')
api.add_resource(TaskStatus, '/task-status/<task_id>')

## Routes

@app.route('/pay', methods=['GET'])
def pay():
    base64_url = request.args.get('pdf') 
    pdf_url = base64.urlsafe_b64decode(base64_url).decode('utf-8')

    return redirect(pdf_url)

@app.route('/')
def login_page():
    if 'google_token' in session:
        return redirect('/dashboard')
    else:
        return render_template('index.html')

@app.route('/dashboard')
@login_required
def index():
    user_full_name = session.get('user_full_name')
    user_id = session.get('id')  

    return render_template('home.html', full_name=user_full_name)

@app.route('/loading')
def loading():
    topic = request.args.get("topic")
    comic = request.args.get('comic')  
    return render_template('loading.html', topic=topic, comic_style=comic)

@app.route('/comic')
def comic_view():
    topic = request.args.get("topic")

    base64_encoded_comic_list = request.args.get('img')
    decoded_comic_list = base64.urlsafe_b64decode(base64_encoded_comic_list).decode('utf-8')
    comic_list = decoded_comic_list.split(',') 
    pdf_link  = request.args.get("pdf")
    return render_template('comic.html', topic=topic, comic_list=comic_list, pdf_link=pdf_link)

@app.route('/login')
def login():
    if "127.0.0.1" in request.url_root or "localhost" in request.url_root:
        return redirect('dashboard')
    return redirect('https://www.witeso.com/login?redirect=https://storyscape.witeso.com')

@app.route('/logout')
def logout():
    if "127.0.0.1" in request.url_root or "localhost" in request.url_root:
        return redirect(request.url_root)
    return redirect("https://www.witeso.com/logout?redirect=https://storyscape.witeso.com")

if __name__ == '__main__':
    app.run(debug=True)
