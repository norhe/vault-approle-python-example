import hvac
import os
from config_helper import get_option

client = None


def get_vault_client():
    global client
    if not client:
        auth_to_vault()
        return client
    elif client and client.is_authenticated():
        try:
            # test that we are still authed
            client.read('fake/path/test')
            return client
        except InvalidRequest: # we are not longer authed
            auth_to_vault()
            return client


def auth_to_vault():
    # TODO: plumb in consul here
    vault_addr = get_option('vault', 'url')
    vault_port = get_option('vault', 'port')

    if not vault_port or not vault_addr:
        raise Exception('Please provide values for vault_addr and vault_port in the config.ini.')

    global client
    address = str(vault_addr) + ':' + str(vault_port)
    print 'Initializing client with address: ' + address
    client = hvac.Client(url=address)
    get_token()


# assumes appId was written to path by provision-er
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
    role_id = get_option('vault', 'role_id')
    if not role_id:
        role_id = read_id_disk(get_option('vault', 'role_id_disk_path'))
    if not role_id:
        role_id = read_id_env(get_option('vault', 'role_id_env')) # this could come from config, or be hardcoded for some obscurity
    if not role_id:
        raise Exception('Role_id must be provided in config, disk, or env.  Aborting')
    return role_id


def get_secret_id():
    secret_id = get_option('vault', 'secret_id')
    if not secret_id:
        secret_id = read_id_disk(get_option('vault', 'secret_id_disk_path'))
        print "Found on disk: " + secret_id
    if not secret_id:
        secret_id = read_id_env(get_option('vault', 'secret_id_env')) # this could come from config, or be hardcoded for some obscurity
        print "found env var: " + secret_id
    if not secret_id:
        raise Exception('Secret_id must be provided in config, disk, or env.  Aborting')
    return secret_id


# This is meant to interact with the approle backend
def get_token():
    try:
        role_id = get_role_id()
        print 'Role_id = ' + str(role_id)
        secret_id = get_secret_id()
        print 'Secret_id = ' + str(secret_id)
        print 'Authenticating with role_id and secret_id: ' + str(role_id) + '::' + str(secret_id)
        # retrieve our token, call caches the token
        global client
        resp = client.auth_approle(role_id, secret_id)
        if resp and resp['auth'] and resp['auth']['client_token']:
            client.token = resp['auth']['client_token']
        else:
            print "We did not receive the token in the response:\n" + str(resp)
        print 'Successfully authenticated!'
    except Exception as ex:
        raise Exception('An error occurred initializing vault client:' + ex.message)
