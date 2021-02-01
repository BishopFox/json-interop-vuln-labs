from flask import Flask
import mysql.connector
import time

app = Flask(__name__)

mydb = None
while mydb is None:
    time.sleep(1)
    mydb = mysql.connector.connect(
        host="mysql",
        user="root",
        password="bb3cf293a43066428577ac02926cefd0",
        database="demo",
        charset="binary"
    )


@app.route('/')
def index():
    return "Permission API"


@app.route('/permissions/<username>')
def permissions(username):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT r.name FROM users u LEFT JOIN user_roles ur ON u.id = ur.user_id LEFT JOIN roles r ON ur.role_id = r.id WHERE u.name = %s",
                     (username,))

    # Decode binary values to utf-8
    roles = [x[0].decode("utf-8") for x in mycursor.fetchall()]
    if roles:
        return {"roles": roles}
    else:
        return {"Error": "User does not exist"}, 400
