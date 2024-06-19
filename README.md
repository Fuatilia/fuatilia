Fuatilia

```
repo structure
|--app
    |--models
    |--routes
    |--services (modularized functions specifically tied to model implemetation)
    |--utils (generic functions/classes)
    |-- __init_.py
    |--db.py
    |--main.py
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
