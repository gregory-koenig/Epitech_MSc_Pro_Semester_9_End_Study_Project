# Website

Create a virtual environment for Python:
```shell
$ cd web
$ pip install virtualenv
$ python -m venv venv
$ source venv/bin/activate
```

Upgrade `pip` and install packages for the project:
```shell
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```

Run the application:
```shell
(venv) $ flask run
```

To deactivate virtual env:
```shell
(venv) $ deactivate
```
