 FROM python:3

 ENV PYTHONUNBUFFERED 1

 RUN \
  set -x && \
  sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
  apt-get update  && \
  apt-get install -y iptables build-essential && \
  rm /var/lib/apt/lists/* -vfR


 ADD pip.conf ~/.pip/

 RUN mkdir /code
 WORKDIR /code
 ADD requirements.txt /code/
 RUN pip install -r requirements.txt
 ADD . /code/

 RUN \
  set -x && \
  git clone https://github.com/fragglet/c-algorithms && \
  cd c-algorithms && \
  ./autogen.sh && \
  ./configure --prefix=/opt/calg/ && \
  make && \
  make install && \
  rm -rf c-algorithms

ENV  \
    PYTHONPATH="/code/"

RUN  \
    python setup.py build_ext -i

#CMD ["bash","-l"]
#CMD ["python","test.py"]
