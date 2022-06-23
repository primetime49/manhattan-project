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

r.set('active_job_light', 0)
r.set('active_job_medium', 0)
r.set('active_job_heavy', 0)

r.set('active_cat', 'light')

next_turn = {
    'light': 'medium',
    'medium': 'heavy',
    'heavy': 'light'
}
nQueue = 6

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Heruristic to compute the expected compilation time: evaluates number of chars and number of imports 
#Function y = 1 - (1/(1 + x)) is used to obtain a value between 0 and 1 that will be used to place the file in the queue
def eval_complexity(filename):
    file = open('./uploads/' + filename)
    ch = len(file.read())
    imports = file.read().count("include")
    weight = (ch + 1_000 * imports)
    y = 1 - (1 / ( 1 + weight))
    cat = 'heavy'
    if weight < 10_000:
        cat = 'light'
    elif weight < 100_000:
        cat = 'medium'
    return cat


def process_file(filename,cat):
    #increment the currently active job counter
    r.incr('active_job')
    r.incr('active_job_'+cat)
    #pop the job that's about to start
    r.lpop('id_queue_'+cat)
    #testing purpose
    start = time.time()
    #time.sleep(5)
    out = subprocess.run(['g++', '-pthread', '-O3', './uploads/' + filename, '-o', './uploads/results/' + filename.split('.')[0]], capture_output=True, text=True)
    error = "error" in str(out)
    end = time.time()
    #decrease the active job counter
    r.decr('active_job')
    if int(r.get('active_job_'+cat)) >= (get_cat_limit(cat)+1) or r.llen('id_queue_'+cat) == 0:
        r.set('active_cat', next_turn[cat])
        r.set('active_job_'+cat, 0)
    return (out, start, end, error)  #return the output of the process and the time it took to run


def get_cat_limit(cat):
    if cat == 'light':
        return nQueue-1
    elif cat == 'medium':
        return int(max((nQueue/2)-1,0))
    elif cat == 'heavy':
        return int(max((nQueue/4)-1,0))

def break_queue(cat):
    if int(r.get('active_job')) < nQueue and check_turn() == cat:
        return True
    else:
        return False

def wait_queue(cat):
    # frequently check the file at the head of queue
    while break_queue(cat) == False:
        time.sleep(0.1)
    return int(r.lindex('id_queue_'+cat, 0))

def check_turn():
    curr_turn = str(r.get('active_cat'))[2:-1]
    if r.llen('id_queue_'+curr_turn) == 0:
        r.set('active_cat', next_turn[curr_turn])
    return curr_turn

def push_file(filename, id):
    y = eval_complexity(filename)
    r.rpush('id_queue_' + y, id)
    return y

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
        id = random.randint(1,1_000_000)    # add randomness to filename
        filename = str(id) + "_" + secure_filename(file.filename) #Secure function to prevent path traversal
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cat = push_file(filename, id)
        while int(wait_queue(cat)) != id:
            pass
        out, start, end, error = process_file(filename, cat)
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
        id = random.randint(1,1_000_000)    # generate random token
        cat = push_file(filename, id)
        # if the file at the head of queue is him, then it's his time to get processed (go inside active queue)
        # otherwise continue looping
        while int(wait_queue(cat)) != id:
            pass
        out, start, end, error = process_file(filename, cat)
        if error:
            return '<p style="color:red">Error douring compilation: <b>' + str(out) + '</b></p>'
        else:
            return '' + str(out) + ' ; ' + str(start) + ' ; ' +str(end) + ' ; ' +str(cat) 

@app.route("/empty_queue")
def empty_queue():
    before = int(r.get('active_job'))

    r.delete('id_queue_light')
    r.delete('id_queue_medium')
    r.delete('id_queue_heavy')
    r.delete('id_queue')
    
    r.set('active_job', 0)
    r.set('active_job_light', 0)
    r.set('active_job_medium', 0)
    r.set('active_job_heavy', 0)
    
    r.set('active_cat', 'light')
    return 'Queue length was ' + str(before) + '. Queue is emptied' + ' ; ' + str(int(r.get('active_job_light'))) + ' ; ' +str(int(r.get('active_job_medium'))) + ' ; ' +str(int(r.get('active_job_heavy'))) + ' ; ' + str(int(r.llen('id_queue_light'))) + ' ; ' +str(int(r.llen('id_queue_medium'))) + ' ; ' +str(int(r.llen('id_queue_heavy')))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)