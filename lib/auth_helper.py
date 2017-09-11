import hvac
import os
import file
from config_helper import get_option

# this is bad practice as it could be dumped from memory.  Should
# use a secure string implementation, but Python doens't have one
# that's built in.
token = None
secret_id = None
client = None

def get_vault_client():
    if client and client.is_authenticated():
        try:
            client.read('fake/path/test')
            return client
        except InvalidRequest:
            # TODO: plumb in consul here
            vault_addr = get_option('vault_addr')
            vault_port = get_option('vault_port')

            if not vault_port or not vault_addr:
                raise Exception('Please provide values for vault_addr and vault_port in the config.ini.')

            client = hvac.Client(url=vault_addr + ':' + vault_port)
            get_token(client)
            return client





# assumes appId was written to path by provisioner
def read_id_disk(path):
    try:
        f = open(path, 'r')
        return f.read()
    except IOError:
        print 'ID not found in file'

def read_id_env(key):
    try:
        return os.environ[key]
    except KeyError:
        print 'ID not found in environment'

# precedence: options -> disk -> env
def get_role_id():
    role_id = get_option('vault_role_id')
    if not role_id:
        role_id = read_id_disk('/var/role_id') # this could come from config, or be hardcoded for some obscurity
        if not role_id:
            role_id = read_id_env('VAULT_ROLE_ID') # this could come from config, or be hardcoded for some obscurity
            if not role_id:
                raise Exception('Role_id must be provided in config, disk, or env.  Aborting')
    return role_id

def get_secret_id():
    secret_id = get_option('vault_secret_id')
    if not secret_id:
        secret_id = read_id_disk('/var/secret_id') # this could come from config, or be hardcoded for some obscurity
        if not secret_id:
            secret_id = read_id_env('VAULT_SECRET_ID') # this could come from config, or be hardcoded for some obscurity
            if not secret_id:
                raise Exception('Secret_id must be provided in config, disk, or env.  Aborting')
    return secret_id

# This is meant to interact with the approle backend
def get_token(client):
    try:
        role_id = get_role_id()
        secret_id = get_secret_id(client)
        print 'Authenticating with role_id and secret_id: ' + role_id + '::' + secret_id
        # retrieve our token, call caches the token
        client.auth_approle(role_id, secret_id)
        print 'Successfully authenticated!'
    except:
        raise Exception('An error occurred initializing vault client')
