scgiwsgi
=============

A WSGI server based on scgi_server(http://python.ca/scgi/).


Example
------------

```python
from scgiwsgi import WSGIServer
WSGIServer(application).run(port=7777, max_children=5)
```



Install Prerequisites
----------------------

```
pip install scgi
```
