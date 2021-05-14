import json

import json
from pymongo import MongoClient
import 

db = MongoClient('mongodb+srv://Scaffus:admin@cluster0.3aezx.mongodb.net/test')['user']

collection = db['users']

class User():
    
    def __init__(self, username, password, mail):
        self.username = username
        self.password = password
        self.mail     = mail
        
    def toJson(self):
        return json.dumps(self.__dict__)

toto = User('toto', 'psw', 'gogo@gogo.go')

print(toto.toJson())

# col = db["people"]
# data = {'name': 'Patrick', 'age': 69}
# col.insert_one(data)