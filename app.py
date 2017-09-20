from flask import Flask

import lib.db_helper as db_helper

app = Flask(__name__)


@app.route("/")
def hello():
    return "Welcome!"


@app.route("/get_orders")
def get_orders():
    return db_helper.get_orders()


if __name__ == "__main__":
    app.run()
