FROM ubuntu:trusty

RUN apt-get update
RUN apt-get install -y sqlite3 libsqlite3-dev
RUN apt-get install -y wget
RUN apt-get install -y python
RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python get-pip.py
RUN rm get-pip.py

COPY ./requirements.txt .
COPY ./thor.py .
COPY ./schema.sql .
RUN python -c "print 'hello world'"
RUN sqlite3 thor.db < schema.sql
RUN pip install -r requirements.txt
RUN sqlite3 

EXPOSE 5000

CMD python ./thor.py
