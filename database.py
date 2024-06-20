import pymongo
import credentials as cr
from bson.objectid import ObjectId

client = pymongo.MongoClient(f"mongodb://{cr.USER_NAME}:{cr.PASSWORD}{cr.MONGO_URL[0]}")

# function for fetching available databases
def get_database():
    exclude_databases = ["admin", "local", "config"]
    db_names = client.list_database_names()
    user_created_dbs = [db for db in db_names if db not in exclude_databases]
    return user_created_dbs

# list collections
def list_collections(database_name):
    return list(client[database_name].list_collection_names())

# function for finding documents in database
def find_documents(database, collection, query):
    return list(client[database][collection].find(query))

# function for fetching measurements data based on object ids
def get_measurements(entry_ids, database, collection):
    measurements = []
    documents = {}
    for entry_id in entry_ids:
        object_id = ObjectId(entry_id)
        document = client[database][collection].find_one({"_id": object_id})
        measurements.append(document["pressure_measurements"])
        documents[entry_id] = document
    return measurements, documents
