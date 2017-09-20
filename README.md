# Example Python Application using AppRole with Vault

We will imagine we have a simple Python application that consumes resources from a Mongo database, and presents an API.

The records will be contained in the orders collection in the flask_app database.  We will use Vault
to control access to this resource.

#### Install and configure mongodb:
---

```
mkdir ~/data/flask_app
sudo apt-get install mongodb
mongod --port 27017 --dbpath ~/data/flask_app
```

or

```
docker run --name mongo-server -d mongo -v ~/data/flask-app:/data/db
```

---

#### Connect and add admin user

We need to add a user who can create other users.  We have chosen to use a very permissive role
within Mongo, but you can certainly further limit the access Vault has to the server by choosing
more restrictive roles.  Please see (https://docs.mongodb.com/manual/reference/built-in-roles/#userAdminAnyDatabase)
for more information.


```
mongo --port 27017
or
docker run -it --link mongo-server:mongo --rm mongo sh -c 'exec mongo "$MONGO_PORT_27017_TCP_ADDR:$MONGO_PORT_27017_TCP_PORT/test"'
```

```
use admin
db.createUser(
  {
    user: "admin_user",
    pwd: "password",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
```
---

#### Create our database and collections, and insert a record to initialize them.
---
```
use flask_app
db.createCollection('orders')
db.createCollection('customers')
db.orders.insert({'created_on':Date()})
db.customers.insert({'created_on':Date()})
```

#### Restart mongodb with auth:

---

```
mongod --port 27017 --dbpath ~/data/flask_app --auth
```

#### Add mongodb backend in Vault:

```
vault mount mongodb
```

#### Mount an audit backend so we have some idea what's going on:
```
mkdir -p ~/vault_logs && touch ~/vault_logs/audit.log
vault audit-enable file file_path=~/vault_logs/audit.log
```

#### Tell vault how to connect to mongo:
```
vault write mongodb/config/connection uri="mongodb://admin_user:password@127.0.0.1:27017/admin?ssl=false"
```

#### Configure lease parameters:
```
vault write mongodb/config/lease ttl=1h max_ttl=24h
```

#### Create some roles:
```
vault write mongodb/roles/readonly db=flask_app roles='[ "read" ]'
vault write mongodb/roles/write db=flask_app roles='[ "readWrite" ]'
```


#### Enable the backend:
```
vault auth-enable approle
```

#### Create policies:
```
cat <<EOF > flask_app_role_worker_pol.hcl
path "auth/approle/role/flask_app/secret-id" {
  capabilities = ["read","create","update"]
}
EOF

cat <<EOF > flask_app_role_provisioner_pol.hcl
path "auth/approle/role/flask_app/role-id" {
  capabilities = ['read']
}
EOF

cat << EOF >flask_app_db_readonly_pol.hcl
path "mongodb/flask_app/roles/readonly" {
  capabilities = ['read']
}
EOF

cat << EOF >flask_app_db_readwrite_pol.hcl
path "mongodb/flask_app/roles/write" {
  capabilities = ['read']
}
EOF
```

#### Create the approle:

The idea is a long lived app.  Secret_id does not expire, and the token does get renewed periodically

```
vault write auth/approle/role/flask_app secret_id_ttl=0 \
 token_num_uses=1 token_ttl=61m \
 token_max_ttl=61m  secret_id_num_uses=0
```

#### Retrieve the role_id:
```
vault read auth/approle/role/flaskapp/role-id
```

#### Get a SecretID issued against the AppRole:
```
vault write -f auth/approle/role/flask_app/secret-id
```


### Getting the approleID and secretID to the app

You have some choices.  With approle you need to trust something.  A common workflow
would be to embed the approleID into the machine image using a tool like Packer.  You could
then place the secret id in some directory, into an environment variable, or directly into
the config file using Terraform or after it's deployed using a configuration management tool.