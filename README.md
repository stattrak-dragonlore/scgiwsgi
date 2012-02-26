scgiwsgi
=============

A WSGI server based on scgi_server(http://python.ca/scgi/).


Example
------------

```python
from scgiwsgi import WSGIServer
WSGIServer(application).run(port=4000, max_children=5)
```



Install Prerequisites
----------------------

```
pip install scgi
```


Nginx.conf Example
-------------------

```
location / {
    include scgi_params;
    client_max_body_size 10m;
    scgi_pass localhost:4000;
}
```
