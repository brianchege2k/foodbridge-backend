from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  
# Load configuration from config.py
app.config.from_object('config')
# initialize extensions 


db = SQLAlchemy(app)
migrate = Migrate(app, db)

# import models 
from models import User 

if __name__ == '__main__':
    app.run (debug=True)