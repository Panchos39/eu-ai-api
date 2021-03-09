FROM ubuntu:20.04

ENV TZ=Europe/Kaliningrad
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils git curl unzip wget pkg-config \
    build-essential cmake gcc \
    libopenblas-dev

RUN apt-get install -y --no-install-recommends python3-dev python3-pip python3-tk python3-wheel && \
    pip3 install --no-cache-dir --upgrade pip setuptools && \
    echo "alias python='python3'" >> /root/.bash_aliases && \
    echo "alias pip='pip3'" >> /root/.bash_aliases

# Science libraries and other common packages

RUN pip3 --no-cache-dir install \
    numpy scipy scikit-image pandas seaborn scikit-learn tqdm matplotlib Cython requests

RUN pip3 install --no-cache-dir --upgrade pymongo pika boto3 flask flask_restful
#RUN pip3 install --upgrade tensorflow==2.2.0
#RUN pip3 install --no-cache-dir torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html  
RUN pip3 install --no-cache-dir --upgrade lxml
RUN pip3 install --no-cache-dir --upgrade gunicorn
RUN apt-get clean && apt-get update && apt-get install --fix-missing -y locales tmux
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN pip3 install jupyter jupyterlab
WORKDIR usr/src/flask_app


