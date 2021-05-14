from flask import Flask
from ..app import app
from .models import User

@app.route('/u/register', methods=['GET', 'POST'])
def register():
    pass