FROM python:latest
WORKDIR /usr/src/app
COPY . .
RUN python -m pip install -r requirements.txt
CMD ["python","app.py"]