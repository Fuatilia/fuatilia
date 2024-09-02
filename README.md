Fuatilia

```
repo structure
|--app
    |--apps
        |---(Each app with their models, urls, ....)
    |--settings.py
    |--utils (generic functions/classes)
    |-- __init_.py
    |--asgi.py
    |--wsgi.py
    |--manage.py
|--.dockerignore
|--.gitignore
|--Dockerfile
|--requirements.txt
```

***To run locally*** <br>
`python -m venv venv` <br>
`pip install -r requirements.txt` <br>
`python app/main.py` <br>

***To run on docker*** <br>
`docker build -t <_name_> .` <br>
`docker run -it --net=host <_name_>` <br>

***To run on docker (With OpenTelemetry)*** <br>
`docker compose up --build .` <br>

***To run tests (Locally)***<br>
`python app/manage.py test app/apps` <br>
