from flask_restful import Resource
from resources.models import Recipe


class RecipeList(Resource):
    def get(self):
        r = Recipe.query.order_by(Recipe.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200
