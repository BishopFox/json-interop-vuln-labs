from flask import Flask, request
import requests
import ujson

import os.path
import urllib

app = Flask(__name__)


@app.route('/')
def index():
    return "Admin API"


@app.route('/admin')
def admin():
    username = request.cookies.get("username")
    if not username:
        return {"Error": "Specify username in Cookie"}

    username = urllib.quote(os.path.basename(username))

    url = "http://permissions:5000/permissions/{}".format(username)
    resp = requests.request(method="GET", url=url)

    ret = ujson.loads(resp.text)

    if resp.status_code == 200:
        if "superadmin" in ret["roles"]:
            return {"OK": "Superadmin Access granted"}
        else:
            e = u"Access denied. User has following roles: {}".format(ret["roles"])
            return {"Error": e}, 401
    else:
        return {"Error": ret["Error"]}, 500
