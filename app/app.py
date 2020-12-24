from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from config import Configuration
import json

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)


from resources.RecipeList import RecipeList

app.config.from_object(Configuration)

api.add_resource(RecipeList, '/recipes')
