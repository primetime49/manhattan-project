# The Manhattan project

This project is for Software Performance and Scalability: We're making a queue to handle incoming web requests, like small cities handling big traffic

# Development environment setup 

```bash
git clone https://github.com/primetime49/manhattan-project.git
cd manhattan-project
docker build .  -t manhattan-project
docker run -p 80:5000 -v $PWD/src:/root/app manhattan-project
```

The webserver will listen on port 80, to access it, open a browser and go to http://localhost
