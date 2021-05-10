from flask import Flask, jsonify, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'about': 'hello world!'}

    def post(self):
        json_ = request.get_json()
        return {'you sent': json_}, 201
    
class Names(Resource):
    
    def get(self):
        name_list = []
        
        with open('names.txt', 'r') as names:
            for name in names: name_list.append(name)
            
        return jsonify(name_list)
    
class Cities(Resource):
    
    def get(self):
        city_list = []
        
        with open('cities.txt', 'r') as cities:
            for city in cities: city_list.append(city)
            
        return jsonify(city_list)
    
class RandomNameLName(Resource):
    
    def get(self):
        city_list = []
        name_list = []
        
        with open('cities.txt', 'r') as cities:
            for city in cities: city_list.append(city)
            
        with open('names.txt', 'r') as names:
            for name in names: name_list.append(name)
        
        return jsonify(city_list + name_list)
    
api.add_resource(HelloWorld, '/')
api.add_resource(RandomNameLName, '/get/couples')
api.add_resource(Names, '/get/names')
api.add_resource(Cities, '/get/cities')

if __name__ == '__main__':
    app.run(debug=True)