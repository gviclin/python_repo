import multiprocessing

bind = "127.0.0.1:8000"
workers = 4
#multiprocessing.cpu_count() * 2 + 1
#timout = 80
#graceful_timeout = 2

worker_class="gthread"

#gunicorn -c gunicorn.py myProject.wsgi:application --log-level=debug 


'''
worker_class

    -k STRING, --worker-class STRING
    sync

The type of workers to use.

The default class (sync) should handle most “normal” types of workloads. You’ll want to read Design for information on when you might want to choose one of the other worker classes. Required libraries may be installed using setuptools’ extras_require feature.

A string referring to one of the following bundled classes:

    sync
    eventlet - Requires eventlet >= 0.24.1 (or install it via pip install gunicorn[eventlet])
    gevent - Requires gevent >= 1.4 (or install it via pip install gunicorn[gevent])
    tornado - Requires tornado >= 0.2 (or install it via pip install gunicorn[tornado])
    gthread - Python 2 requires the futures package to be installed (or install it via pip install gunicorn[gthread])

'''
