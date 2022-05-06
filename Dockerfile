FROM ubuntu:latest

RUN apt-get update
RUN apt -yq install \
    wget \
    curl \
    git \
    bash \
    g++ \
    make \
    pip \
    redis-server


RUN pip install Flask flask-restful redis rq
# ADD OTHER Python PACKAGES HERE

# Clean
RUN rm -rf ~/.cache/pip


COPY start.sh /root/start.sh
RUN chmod +x  /root/start.sh

RUN mkdir /root/app

ENTRYPOINT ["/root/start.sh"]
