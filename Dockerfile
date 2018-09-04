FROM python:3.6

# Install python (maybe someday their will be an up to date openjdk-python all in one container)
# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

# runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tcl \
        tk \
    && rm -rf /var/lib/apt/lists/*

## Install mallet (topic modelling library we use)
#
## RUN apt-get update; apt-get upgrade -y
#RUN apt-get update && apt-get install ant mercurial -y && rm -rf /var/lib/apt/lists/*
#WORKDIR /
#RUN wget http://mallet.cs.umass.edu/dist/mallet-2.0.8.tar.gz
#RUN tar -zxvf mallet-2.0.8.tar.gz
#RUN mv mallet-2.0.8 mallet
#WORKDIR /mallet
#RUN pwd
#RUN ls -lah
#RUN ant

# Create the code folder we will be moving the project into

RUN mkdir /code
WORKDIR /code

## Install the compilers a dependancies for the python libraries we need
#
#ADD testing.perf /etc/apt/preferences.d/
#ADD testing.list /etc/apt/sources.list.d/
#
#RUN apt-get update && apt-get install python3/testing python3-pip/testing -y --no-install-recommends
#
#RUN cd /usr/local/bin \
#	&& ln -s idle3 idle \
#	&& ln -s pydoc3 pydoc \
#	&& ln -s python3 python \
#&& ln -s python3-config python-config
#RUN rm /usr/bin/python
#RUN ln -s /usr/bin/python3 /usr/bin/python
#
#RUN apt-get install gcc gfortran python3-dev libblas-dev liblapack-dev -y
#RUN pip3 install setuptools wheel

# Install the libraries (moving these first means that when changing the code it does not effect anything at this step
# So the intermediate container with dependancies can be re-used)

ADD requirements.txt /code/
RUN pip3 install -r requirements.txt

## Download the nltk libraries
#
#RUN apt-get -y install unzip
#
##Let's try this version!
#ENV PATH_TO_NLTK_DATA /root/nltk_data/
#RUN echo $PATH_TO_NLTK_DATA
#RUN apt-get -qq update
#RUN apt-get -qq -y install wget
#RUN wget https://github.com/nltk/nltk_data/archive/gh-pages.zip
#RUN unzip gh-pages.zip -d $PATH_TO_NLTK_DATA
## add below code
#RUN mv $PATH_TO_NLTK_DATA/nltk_data-gh-pages/packages/* $PATH_TO_NLTK_DATA/
#WORKDIR $PATH_TO_NLTK_DATA
#RUN cd tokenizers && unzip punkt.zip
#RUN pwd
WORKDIR /code

# Github broke this for now
# ADD nltk-download.py /code/
# RUN python nltk-download.py
# RUN python -m nltk.downloader -u https://pastebin.com/raw/D3TBY4Mj stopwords wordnet punkt

# Add the rest of the code

ADD . /code/

# Expose the gunicorn port to the outside

EXPOSE 8000

# Run the django web server using gunicorn

CMD ["gunicorn", "scraper_server.wsgi:application", "--log-level=debug", "--bind=0.0.0.0", "--workers=3", "--timeout=30000"]