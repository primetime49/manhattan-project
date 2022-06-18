# The Manhattan project

This project is for Software Performance and Scalability: We're making a queue to handle incoming web requests, like small cities handling big traffic

# Development environment setup (old version)

```bash
git clone https://github.com/primetime49/manhattan-project.git
cd manhattan-project
docker build .  -t manhattan-project
docker run -p 80:5000 -v $PWD/src:/root/app manhattan-project
```

The webserver will listen on port 80, to access it, open a browser and go to http://localhost

# Docker compose (new version w/ redis)
1. sudo docker-compose up

# Tsung
1. tsung -f tsung/http_simple.xml start
2. cd /home/adityo/.tsung/log/20220506-1828 (change the timestamp)
3. perl ~/Downloads/tsung-1.7.0/src/tsung_stats.pl (Change to your own dir)
4. google-chrome report.html
