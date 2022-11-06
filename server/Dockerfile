FROM python:3.9-alpine
EXPOSE 8080
COPY . /server
WORKDIR /server

RUN python -m pip install -r requirements.txt

CMD ["python", "server/main.py"]