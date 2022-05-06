from flask import Flask
from flask_restful import Resource, Api
import sys
import subprocess
import random
import time
import redis
from rq import Queue

app = Flask(__name__)
api = Api(app)
port = 5000

r = redis.Redis(host='redis', port=6379)
q = Queue(connection=r)
nQueue = 8

def process_file(filename):
    #increment the currently active job counter
    r.incr('active_job')
    #testing purpose
    start = time.time()
    #todo: change to actual c++ compiling
    #w = random.uniform(5,8)
    out = subprocess.run(['g++', '-pthread', '-O3', './testcases/' + filename, '-o', './testcases/results/' + filename.split('.')[0]], capture_output=True, text=True)

    #pop the job that's about to start
    r.lpop('id_queue')
    #time.sleep(w)
    end = time.time()

    #decrease the active job counter
    r.decr('active_job')
    return (out, start, end)

def wait_queue():
    while int(r.get('active_job')) >= nQueue:
        time.sleep(0.1)
    return int(r.lindex('id_queue', 0))

'''for i in range(nQueue):
    worker = threading.Thread(target=process_file, args=(i, main_queue,))
    worker.setDaemon(True)
    worker.start()''' 

if sys.argv.__len__() > 1:
    port = sys.argv[1]
print("Api running on port : {} ".format(port))

class HomePage(Resource):
    def get(self):
        r.set('active_job', 0)
        return 'Hello '

class EnqueueJob(Resource):
    def get(self, filename):
        id = random.randint(1,1000000)
        r.rpush('id_queue', id)
        while wait_queue() != id:
            pass
        #q.enqueue(process_file)
        
        w, start, end = process_file(filename)

        res = '' + str(w) + ' ; ' + str(start) + ' ; ' +str(end) 
        return res

class EmptyQueue(Resource):
    def get(self):
        r.delete('id_queue')
        r.set('active_job', 0)
        return 'Queue is emptied'


api.add_resource(HomePage, '/')
api.add_resource(EnqueueJob, '/enqueue/<filename>')
api.add_resource(EmptyQueue, '/empty')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
    r.set('active_job', 0)
    