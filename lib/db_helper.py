from pymongo import MongoClient
from config_helper import get_option
from auth_helper import get_vault_client

# connect
# http://api.mongodb.com/python/current/tutorial.html#making-a-connection-with-mongoclient
# auth examples
# http://api.mongodb.com/python/current/examples/authentication.html?highlight=authentication#delegated-authentication


db_client = None

def init_db_client(uname, pword):
    global db_client
    if db_client is None:
        # plumb in consul
        db_url = get_option('db, ''db_url')
        db_port = int(get_option('db', 'db_port'))

        if not db_url or not db_port:
            print "Please provide values for db_url and/or db_port in the config.ini"
            return

        db_client = MongoClient(
            host=db_url,
            port=db_port,
            username=uname,
            password=pword,
            #authSource = 'admin',
            #authMechanism='SCRAM-SHA-1')
        )

# We use Vault to retrieve ephemeral auth info for the Mongo DB.
def auth_db():
    vault_client = get_vault_client()
    # Get vault path from Consul?
    resp = vault_client.read('/mongdb/creds/readonly')
    if resp and resp['data']:
        uname = resp['data']['username']
        pword = resp['data']['password']
        db = resp['data']['db']
        print "Retrieved uname::pword::db => " + uname + "::" + pword + "::" + db
        if uname and password:
            init_db_client(uname, pword)
        else:
            print 'Did not get username or password!'

    #db_client.auth()

# If we hav
def get_orders():
    global db_client
    tries = 0
    results = None
    while tries < 2:
        if db_client is None:
            auth_db()
        try:
            results = _get_orders()
            tries = 2
        except OperationFailure:
            # If we're here auth may have failed.  Our creds could have expired
            db_client = None # invalidate the client
            count += 1
        except Exception as ex:
            print "Exception received: " + ex
    return results


def _get_orders():
    # could use Consul to find these values
    db = db_client["flask_app"] # get db
    col = db["orders"]          # get collection
    return list(col.find({}))   # naively return all records
