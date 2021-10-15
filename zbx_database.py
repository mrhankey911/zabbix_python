import psycopg2, argparse, os,yaml, json
from dotenv import load_dotenv
from pathlib import Path

# Reading config file
with open("/usr/local/share/zabbix-agent/config/uniswap2_exec_config.yaml", "r") as yamlfile:
    config = yaml.load(yamlfile, Loader=yaml.FullLoader)

# Define arguments
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--discovery", action='store_true', help="Create dsicovery items in JSON for zabbix")
parser.add_argument("-i", "--item", type=str, help="Getting item from script argument (zabbix item)")
args = parser.parse_args()

####################################################################
#####                  Script Function's part                  #####
####################################################################

# Create discovery for zabbix
def get_discovery():
    dict_databases_keys = []
    dict_item_keys = []
    items = []
    for _ in range(len(config['databases'])):
        dict_databases_keys.append(list(config['databases'][_].keys())[0])
        dict_item_keys.append(list(config['databases'][_][dict_databases_keys[_]].keys()))
        for i in range(len(config['databases'][_][dict_databases_keys[_]])):
            if dict_item_keys[_][i] != 'dotenv_path' and dict_item_keys[_][i] != 'database_connection_setting':
                items.append( {"{#DATABASE}": ''.join(dict_databases_keys[_]), "{#ARGUMENT}": ''.join(dict_item_keys[_][i])})
    discovery = { "data" : items}
    print(json.dumps(discovery))

# Function which open database connection and do SQL Queries
def do_sql_queries():

    item = args.item.partition(':')
    current_database = item[0]
    current_item = item[2]

    dict_databases_keys = []
    for _ in range(len(config['databases'])):
        dict_databases_keys.append(list(config['databases'][_].keys())[0])

    current_id = dict_databases_keys.index(current_database)
    current_query = config['databases'][current_id][current_database][current_item]['query']
    database_conn_settings = config['databases'][current_id][current_database]['database_connection_setting']
    env_path = config['databases'][current_id][current_database]['dotenv_path']

    # Define .env
    dotenv_path = Path(env_path)
    load_dotenv(dotenv_path=dotenv_path)

    # Set up database connecton
    con = psycopg2.connect(
    database=os.getenv(database_conn_settings['database']),
    user=os.getenv(database_conn_settings['user']),
    password=os.getenv(database_conn_settings['password']),
    host=os.getenv(database_conn_settings['host']),
    port=os.getenv(database_conn_settings['port']))

    # Do SQL requests
    with con:
        with con.cursor() as curs:
            curs.execute(current_query)
            rows = curs.fetchall()

    # Print out sql query resultx
    for row in rows:
        print(row[0])

    # Close connection
    con.close()

def main():
    if args.discovery:
        get_discovery()
    else:
        do_sql_queries()

if __name__ == '__main__':
    main()
