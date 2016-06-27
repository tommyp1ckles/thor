# Thor is a simple monitoring notification service

# Basic Imports
import simplejson as json
import os
import sqlite3
import requests
from termcolor import colored

from flask import Flask, g, request, render_template
# Flask Setup
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, "thor.db"),
    SECRET_KEY='development key',
    DEBUG=True,
))

databaseName = "./thor.db"
indent = "  "
def db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(databaseName)
    return db

# Twilio API
from twilio.rest import TwilioRestClient

def twilioToken():
    sid = os.environ.get("TWILIO_SID")
    token = os.environ.get("TWILIO_TOKEN")
    number = os.environ.get("TWILIO_NUMBER")
    if sid is None or token is None:
        return None
    tt = {
        "ACCOUNT_SID": sid,
        "TOKEN": token,
        "NUMBER": number,
    }
    return tt

def APIToken():
    return os.environ.get("THOR_API_KEY")

# Error types
# Exception designed to be thrown when the exception is to be passed onto the
# front ent.
class SafeException(Exception):
    def __init__(self, value):
        self.Value = value
    def __str__(self):
        return repr(self.Value)

# This exception is also **SAFE**
class AuthenticationError(Exception):
    def __init__(self, value):
        self.Value = value
    def __str__(self):
        return repr(self.Value)

# Checks to see if a dict contains all specified keys.
def containsKeys(m, *keys):
    for key in keys:
        if key not in m:
            return key
    return None

def mapResult(row, keys):
    res = {}
    for i in range(0, len(keys)):
        res[keys[i]] = row[i]
    return res

def sendSMSNotification(to_number, content):
    token = twilioToken()
    if token is None:
        raise SafeException("No twilio token set")
    try:
        client = TwilioRestClient(token["ACCOUNT_SID"], token["TOKEN"])
        client.messages.create(to=to_number, _from=token["NUMBER"],
            body=content)
    except Exception as err:
        raise err

def sendEmailNotification(to_email, content):
    ret = requests.post(
        "https://api.mailgun.net/v3/"+server+"/messages",
        auth=("api", token),
        data={
            "from": "Euclid Monitoring System>",
            "to": recipients,
            "subject": subject,
            "text": content,
        },
    )

# Handlers
def authenticateRequest(rawdata):
    if APIToken() is None:
        raise SafeException("No API token defined, contact administrator")
        return False
    data = json.loads(rawdata)
    missingKey = containsKeys(data, "token")
    if missingKey is not None:
        raise SafeException("API token required.")
        return False
    if data["token"] != APIToken():
        raise AuthenticationError("Incorrect API token.")
        return False
    return True

def handleEvent(rawdata):
    data = json.loads(rawdata)
    missingKey = containsKeys(data, "node", "content", "defcon")
    if missingKey is not None:
        raise SafeException("Missing field: "+missingKey)
        return
    else:
        conn = db()
        conn.row_factory = sqlite3.Row
        cursor = conn.execute('''
            SELECT * FROM users
        ''')
        for user in cursor:
            keys = user.keys()
            u = mapResult(user, keys)
            if data["defcon"] >= u["defcon"]:
                try:
                    sendSMSNotification(
                        u["phone"],
                        "Warning: node '%s' is at Defcon %s. \n Description: %s" % \
                            (data["node"], data["defcon"], data["content"]),
                    )
                except Exception as err:
                    print("Error: Error while sending Twilio message: "+str(err))
                    raise err

def createUser(rawdata):
    try:
        data = json.loads(rawdata)
    except:
        raise SafeException("Error parsing JSON data")
    missingKey = containsKeys(data, "name", "email", "phone", "defcon")
    if missingKey is not None:
        raise SafeException("Missing field: "+missingKey)
        return
    else:
        conn = db()
        cursor = conn.execute('''
            INSERT INTO users (name, email, phone, defcon)
            VALUES (?, ?, ?, ?)
        ''',
        (data["name"], data["email"], data["phone"], data["defcon"]))
        conn.commit()
        cursor.close()

def updateUser(rawdata):
    try:
        data = json.loads(rawdata)
    except:
        raise SafeException("Error parsing JSON data")
    missingKey = containsKeys(data, "id")
    if missingKey is not None:
        raise SafeException("Missing field: "+missingKey)
        return
    else:
        conn = db()
        if "email" in data:
            cursor = conn.execute(
                    "UPDATE users SET email = ? WHERE id = ?",
                    (data["email"],data["id"]),
            )
        if "phone" in data:
            cursor = conn.execute(
                    "UPDATE users SET phone = ? WHERE id = ?",
                    (data["phone"],data["id"])
            )
        if "defcon" in data:
            cursor = conn.execute(
                    "UPDATE users SET defcon = ? WHERE id = ?",
                    (data["defcon"],data["id"])
            )
        conn.commit()

def getUsers(data):
    # Stub handler
    return "stub :/"

# Return codes
internalServerError = 500
unauthorizedRequest = 401
badRequest = 400
OK = 200

# Convenience function runs handler and handles all the error handling
# and authentication.
def runHandler(fn, request):
    try:
        data = json.loads(request.data)
        authenticateRequest(request.data)
        fn(request.data)
        return "", OK
    except AuthenticationError as err:
        return str(err), unauthorizedRequest
    except json.JSONDecodeError as err:
        return "Error decoding JSON", badRequest
    except SafeException as err: # Only for errors safe to be thrown to frontend.
        return str(err), badRequest
    except Exception as err:
        print(colored("Server Error: " + str(err), "red"))
        return "Internal server error", internalServerError

# API
@app.route("/api/events", methods=["POST"])
def events():
    if request.method != "POST":
        return 404
    else:
        return runHandler(handleEvent, request)

@app.route("/api/users", methods=["POST", "GET", "PUT"])
def users():
    if request.method == "GET":
        return runHandler(getUsers, request)
    elif request.method == "POST":
        return runHandler(createUser, request)
    elif request.method == "PUT":
        return runHandler(updateUser, request)

if __name__ == "__main__":
    app.run()
