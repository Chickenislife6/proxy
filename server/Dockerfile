FROM python:3.9-alpine
EXPOSE 8080
COPY . /
WORKDIR /

RUN python -m pip install -r requirements.txt

CMD ["python", "main.py"]