#!/bin/bash
echo "Starting webserver"

cd /root/app

export FLASK_APP=webserver
export FLASK_ENV=development

# Run webserver
flask run --host=0.0.0.0