from flask import Flask, request
import jsonschema
from jsonschema.exceptions import SchemaError
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
        charset="binary",
    )

cursor = mydb.cursor()
# Reset database
cursor.execute("DROP DATABASE demo")
cursor.execute("CREATE DATABASE demo CHARACTER SET binary")
cursor.execute("USE demo")

# create tables
cursor.execute("CREATE TABLE users (id int NOT NULL AUTO_INCREMENT primary key, name varchar(255))")
cursor.execute("CREATE TABLE roles (id int NOT NULL AUTO_INCREMENT primary key, name varchar(255))")
cursor.execute("CREATE TABLE user_roles (id int NOT NULL AUTO_INCREMENT primary key, user_id int, role_id int)")
cursor.execute("INSERT INTO roles (name) VALUES (\"superadmin\")")
mydb.commit()


@app.route('/')
def index():
    return "User API"

# /user/create


userschema = {
    "type": "object",
    "properties": {
        "user": {"type": "string"},
        "roles": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["user", "roles"]
}


@app.route('/user/create', methods=["POST"])
def createUser():
    data = request.get_json(force=True)
    try:
        jsonschema.validate(instance=data, schema=userschema)
    except SchemaError as e:
        return {"Error": "Invalid Request: " + e}, 400

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM users WHERE name = %s", (data["user"],))

    if len(list(cursor.fetchall())) > 0:
        return {"Error": "User already exists"}, 400

    forbiddenroles = ["superadmin"]

    cursor.execute("SELECT id, name FROM roles")
    dbroles = cursor.fetchall()

    for role in data["roles"]:
        # Convert to bytes before comparison
        role = role.encode("utf-8")
        # compare against name field
        if role not in [x[1] for x in dbroles]:
            return {"Error": u"Role '{}' does not exist".format(role)}, 404
        if role in forbiddenroles:
            return {"Error": u"Assignment of internal role '{}' is forbidden".format(role)}, 401

    cursor.execute("INSERT INTO users (name) VALUES (%s)", (data["user"],))
    mydb.commit()

    userid = cursor.lastrowid
    for role in data["roles"]:
        # Convert to bytes before comparison
        role = role.encode("utf-8")
        for i in range(len(dbroles)):
            if role == dbroles[i][1]:
                cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                               (userid, dbroles[i][0]))

    mydb.commit()

    return {"OK": u"Created user '{}'".format(data["user"])}

# /role/create


roleschema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"}
    },
    "required": ["name"]
}


@app.route('/role/create', methods=["POST"])
def createRole():
    data = request.get_json(force=True)
    try:
        jsonschema.validate(instance=data, schema=roleschema)
    except SchemaError:
        return {"Error": "Invalid Request"}, 400

    rolename = data["name"]

    cursor = mydb.cursor()
    cursor.execute("SELECT name FROM roles WHERE name = %s", (rolename,))

    if len(list(cursor.fetchall())) == 0:
        cursor.execute("INSERT INTO roles (name) VALUES (%s)", (rolename,))
        mydb.commit()
    else:
        return {"Error": "Role already exists"}, 400
    return {"OK": u"Created role '{}'".format(rolename)}
