FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN mkdir -p /home/forum
ENV HOME=/home/forum
ENV APP_HOME=/home/forum/app
RUN mkdir $APP_HOME

WORKDIR $APP_HOME

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . $APP_HOME

EXPOSE 8000