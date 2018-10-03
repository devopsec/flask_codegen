import os, socket

FQDN=socket.getfqdn()
if FQDN == None or FQDN == "":
    FQDN = socket.gethostname()

# REST server settings
API_SERVER_HOST="0.0.0.0"
API_SERVER_PORT="7777"
API_SERVER_URL="http://{host}:{port}".format(host=API_SERVER_HOST, port=API_SERVER_PORT)

# MySQL settings
DB_TYPE='mysql'
DB_HOST='localhost'
DB_PORT='3306'
DB_NAME="tspace"
DB_USER="root"
DB_PASS=""

# Specify the deployment environment
# Possible values = (DEV,TEST, PROD)
ENV='DEV'


# Set paths dynamically
ROOT_DIR=os.path.abspath(os.sep)
PROJECT_ROOT_DIR=os.path.abspath(os.path.dirname(__file__))
API_DIR=os.path.join(PROJECT_ROOT_DIR, "api")

SERVER_DIR=os.path.join(PROJECT_ROOT_DIR, "server")
SERVER_PLUGINS_DIR=os.path.join(SERVER_DIR, "uwsgi-emperor", "plugins")
SERVER_API_LOAD_FILE=os.path.join(SERVER_DIR, "uwsgi-emperor", "vassals", "rest_server.ini")
SERVER_API_CONF_FILE=os.path.join(SERVER_DIR, "nginx", "sites-available", "rest_server.conf")

LOG_DIR=os.path.join(ROOT_DIR, "var", "log", "tspace")
API_LOG_FILE=os.path.join(LOG_DIR, "api.log")
DB_LOG_FILE=os.path.join(LOG_DIR, "db.log")

