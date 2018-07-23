#!/usr/bin/env python
#https://stackoverflow.com/questions/13386681/streaming-data-with-python-and-flask
import time
from flask import Flask, Response

app = Flask(__name__)


def stream_template(template_name, **context):
    # http://flask.pocoo.org/docs/patterns/streaming/#streaming-from-templates
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # uncomment if you don't need immediate reaction
    ##rv.enable_buffering(5)
    return rv


@app.route('/')
def index():
    def g():
        num = 0
        while True:
            time.sleep(.1)  # an artificial delay
            num +=1
            yield num, num+1
    return Response(stream_template('index2.html', data=g()))

if __name__ == "__main__":
    app.run(host='127.1.1.1', debug=False, threaded=True, port=8000)
