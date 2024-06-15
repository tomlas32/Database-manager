import pymongo
import credentials as cr

client = pymongo.MongoClient(f"mongodb+srv://{cr.USER_NAME}:{cr.PASSWORD}{cr.MONGO_URL[0]}")

# function for fetching available databases
def get_database():
    return list(client.list_database_names())

# list collections
def list_collections(database_name):
    return list(client[database_name].list_collection_names())