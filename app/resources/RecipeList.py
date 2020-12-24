from flask_restful import Resource
from flask import jsonify
from resources.models import Recipes


class RecipeList(Resource):
    def get(self):
        recipes = Recipes.query.order_by(Recipes.id.desc()).all()
        results = [ob.as_json() for ob in recipes]
        return jsonify(results)
