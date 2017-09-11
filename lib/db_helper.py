from pymongo import MongoClient
from config_helper import get_option
from auth_helper import get_vault_client

# connect
# http://api.mongodb.com/python/current/tutorial.html#making-a-connection-with-mongoclient
# auth examples
# http://api.mongodb.com/python/current/examples/authentication.html?highlight=authentication#delegated-authentication

db_client = None

def init_db_client(uname, pword):
    if not db_client:
        db_url = get_option('db_url')
        db_port = int(get_option('db_port'))

        if not db_url or not db_port:
            print "Please provide values for db_url and/or db_port in the config.ini"
            return

        db_client = MongoClient(host=db_url, port=db_port, username=uname, password=pword)

def auth_db():
    vault_client = get_vault_client()
    # Get vault path from Consul?
    resp = vault_client.read('/mongdb/creds/readonly')
    if resp and resp['data']:
        uname = resp['data']['username']
        pword = resp['data']['password']
        db = resp['data']['db']
        if uname and password:
            init_db_client(uname, pword)
    #db_client.auth()



def get_customers():
    db_client.
