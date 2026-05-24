FROM python:3.13.13-alpine3.23
WORKDIR /usr/src/app
COPY . .
RUN python -m pip install -r requirements_prod.txt
CMD ["python","app.py"]