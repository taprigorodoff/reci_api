from flask_restful import Resource
from flask import send_from_directory
from resources.models import Recipe


class RecipeDetail(Resource):
    def get(self, id):
        recipe = Recipe.query.filter(Recipe.id == id).first_or_404()
        return recipe.as_full_json(), 200


class RecipeImg(Resource):
    def get(self, id):
        response = send_from_directory(directory='images/', filename='{}.jpg'.format(id))
        return response
