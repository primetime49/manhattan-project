from flask import Flask, render_template, request, send_from_directory
import subprocess
import random
import time
import redis
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'cpp', 'c'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
port = 5000

r = redis.Redis(host='redis', port=6379)
r.set('active_job', 0)
nQueue = 4

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Heruristic to compute the expected compilation time: evaluates number of chars and number of imports 
#Function y = 1 - (1/(1 + x)) is used to obtain a value between 0 and 1 that will be used to place the file in the queue
#An overtake count is computed to avoid starvation of heavy jobs: it represents the maximum number of jobs that can overtake the current one. When overtake limit is reached the job wont be overtaken any more
#Overtake count is computed as the product of current queue size and y of current job: this way light jobs will be overtaken less often than heavy ones
def eval_complexity(filename):
    file = open('./uploads/' + filename)
    ch = len(file.read())
    imports = file.read().count("include")
    weight = (ch + 1000 * imports)
    y = 1 - (1 / ( 1 + weight))
    max_overtake = y * r.llen('id_queue')
    return (y, max_overtake)


def process_file(filename):
    #increment the currently active job counter
    r.incr('active_job')
    #pop the job that's about to start
    r.lpop('id_queue')
    #testing purpose
    start = time.time()
    out = subprocess.run(['g++', '-pthread', '-O3', './uploads/' + filename, '-o', './uploads/results/' + filename.split('.')[0]], capture_output=True, text=True)
    error = "error" in str(out)
    end = time.time()
    #decrease the active job counter
    r.decr('active_job')
    return (out, start, end, error)  #return the output of the process and the time it took to run


def wait_queue():
    # frequently check the file at the head of queue
    while int(r.get('active_job')) >= nQueue:
        time.sleep(0.1)
    return str(r.lindex('id_queue', 0))

def push_file(filename):
    id = random.randint(1,1000000)
    y, comp = eval_complexity(filename)
    xid = (str(id)+'_'+str(y))
    r.rpush('id_queue', xid)
    return id

@app.route("/")
def homepage():
    return render_template('index.html')


@app.route("/upload", methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files: # check if the post request has the file part
            return '<p style="color:red">File not sent</b></p>'
        file = request.files['file']
        if file.filename == '': # If the user does not select a file, the browser submits an empty file without a filename.
            return '<p style="color:red">File is empty</b></p>'
        if file and not allowed_file(file.filename): # check if the file is an allowed extension
            return '<p style="color:red">File not supported</b></p>'
        id = push_file(filename)
        filename = str(id) + "_" + secure_filename(file.filename) #Secure function to prevent path traversal
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        while int(wait_queue().split('_')[0][2:]) != id:
            pass
        out, start, end, error = process_file(filename)
        if error:
            return '<p style="color:red">Error douring compilation: <b>' + str(out) + '</b></p>'
        else:
            return 'Succesfully compiled <b>' + file.filename + '</b> in '+ str(round(end - start, 2)) +' seconds <br><br><a class="btn" id="dowload-btn" style="width:100%" download="/uploads/'+ filename.split('.')[0] + '" href="/uploads/'+ filename.split('.')[0] + '"> Download </a>'


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(app.config['UPLOAD_FOLDER'], 'results')
    return send_from_directory(uploads, filename, as_attachment=True)

@app.route('/enqueue/<path:filename>', methods=['GET'])
def enqueue(filename):
        id = push_file(filename)
        # if the file at the head of queue is him, then it's his time to get processed (go inside active queue)
        # otherwise continue looping
        while int(wait_queue().split('_')[0][2:]) != id:
            pass
        out, start, end, error = process_file(filename)
        if error:
            return '<p style="color:red">Error douring compilation: <b>' + str(out) + '</b></p>'
        else:
            return '' + str(out) + ' ; ' + str(start) + ' ; ' +str(end) 

@app.route("/empty_queue")
def empty_queue():
    before = int(r.get('active_job'))
    r.delete('id_queue')
    r.set('active_job', 0)
    return 'Queue length was ' + str(before) + '. Queue is emptied'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)