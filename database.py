import pymongo
import credentials as cr

client = pymongo.MongoClient(f"mongodb+srv://{cr.USER_NAME}:{cr.PASSWORD}{cr.MONGO_URL[0]}")

# function for fetching available databases
def get_database():
    exclude_databases = ["admin", "local", "config"]
    db_names = client.list_database_names()
    user_created_dbs = [db for db in db_names if db not in exclude_databases]
    return user_created_dbs

# list collections
def list_collections(database_name):
    return list(client[database_name].list_collection_names())
