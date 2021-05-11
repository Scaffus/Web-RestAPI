import pymongo

client = pymongo.MongoClient('mongodb+srv://Scaffus:admin@cluster0.3aezx.mongodb.net/test')

db = client["db"]

col = db["people"]
data = {'name': 'Patrick', 'age': 69}
col.insert_one(data)