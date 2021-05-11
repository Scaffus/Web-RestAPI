from flask import Flask, render_template, request
import pymongo

app = Flask(__name__)
client = pymongo.MongoClient()

db = client['database']

@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        
        name = request.form['name']
        last_name = request.form['last_name']
        
        return render_template('index.html', form=False, name=name, last_name=last_name)
    
    return render_template('index.html', form=True)


if __name__ == '__main__':
    app.run(debug=True)