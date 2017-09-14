from flask import Flask
from datetime import datetime

import lib.db_helper as db_helper
import os
import hvac

app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome!"

@app.route("/get_orders")
def get_orders():
    print "In get_orders"
    return db_helper.get_orders()

if __name__ == "__main__":
    app.run()
