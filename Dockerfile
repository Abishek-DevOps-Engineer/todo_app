FROM python:3.13.13-alpine3.23
WORKDIR /usr/src/app
COPY requirements_prod.txt .
RUN python -m pip install -r requirements_prod.txt
COPY . .
CMD ["python","app.py"]
