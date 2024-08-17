FROM python:3.12-slim-bookworm
WORKDIR /fuatilia
COPY requirements.txt ./
RUN mkdir logs
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
EXPOSE 8000
ENTRYPOINT ["python" , "app/manage.py" , "runserver" , "0.0.0.0:8000"]
