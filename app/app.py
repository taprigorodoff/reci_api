from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from config import Configuration
import json

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
app.config.from_object(Configuration)

from models import Recipes


class RecipeList(Resource):
    def get(self):
        recipes = Recipes.query.order_by(Recipes.id.desc()).all()
        results = [ob.as_json() for ob in recipes]
        return jsonify(results)


api.add_resource(RecipeList, '/recipes')
