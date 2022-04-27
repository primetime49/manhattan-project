from flask import Flask, request
from flask_restful import Resource, Api
import sys
import os
import subprocess
from queue import Queue

app = Flask(__name__)
api = Api(app)
port = 5000

if sys.argv.__len__() > 1:
    port = sys.argv[1]
print("Api running on port : {} ".format(port))

class topic_tags(Resource):
    def get(self):
        system = Queue(5)
        system.append_queue('a')
        return system.queue_job()


api.add_resource(topic_tags, '/')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)