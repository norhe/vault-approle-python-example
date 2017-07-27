from flask import Flask
from datetime import datetime

import os
import hvac

def initialize_vault_client(vault_addr, vault_token):
    if not vault_token:
        env_token = os.environ['VAULT_TOKEN']
        if env_token:
            vault_token = env_token
    
    if not url:
        vault_addr = 'http://locahost:8200'
    
    if not vault_token:
        return hvac.Client(url=vault_addr)
    else
        return hvac.Client(url=vault_addr, vault_token)
        

app = Flask(__name__)

@app.route("/")
def main(vault_addr, vault_token):
    client = initialize_vault_client(vault_addr, vault_token)
    client.write('secret/flask_app', value='secret from ' + str(datetime.now()))
    :wq

    return "Welcome!"

if __name__ == "__main__":
    app.run()
