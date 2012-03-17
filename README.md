scgiwsgi
=============

A WSGI server based on scgi_server(http://python.ca/scgi/).


Example
------------

```python
from scgiwsgi import WSGIServer
from yourapp import application

WSGIServer(application).run(port=4000, max_children=5)
```



Installation
----------------------

```
pip install scgiwsgi
```


Nginx.conf Example
-------------------

```
location / {
    include scgi_params;
    scgi_pass localhost:4000;
}
```
