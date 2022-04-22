FROM ubuntu:latest

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt -yq install \
    wget \
    curl \
    git \
    bash \
    g++ \
    make \
    pip \
    firejail


RUN pip install Flask flask-restful
# ADD OTHER Python PACKAGES HERE

# Clean
RUN rm -rf ~/.cache/pip


COPY start.sh /root/start.sh
RUN chmod +x  /root/start.sh

RUN mkdir /root/app

ENTRYPOINT ["/root/start.sh"]
