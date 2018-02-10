from flask import Flask
from flask import request
import json

app = Flask(__name__)

@app.route('/', methods=['POST',])
def publish():
    d = request.get_json(force=True)
    try:
        #assert d['token'] == u'egh8utahl1MaeQueel4eengievahnaif'
        pass
    except (KeyError, AssertionError):
        flask.abort(400)

    from sign_update import update
    update(d['message'])
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
