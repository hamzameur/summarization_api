FROM python:3.8-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV FLASK_APP=summarization_api/views.py
COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]