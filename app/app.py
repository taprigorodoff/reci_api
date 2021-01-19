from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from config import Configuration

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)


from resources.Recipe import RecipeDetail, RecipeImg, RecipeList
from resources.Ingredient import IngredientList, IngredientDetail
from resources.Ingredient import StoreSectionList, StoreSectionDetail

app.config.from_object(Configuration)

api.add_resource(RecipeList, '/recipe')

api.add_resource(RecipeDetail, '/recipe/<id>')
api.add_resource(RecipeImg, '/recipe/img/<id>')

api.add_resource(IngredientList, '/ingredient')
api.add_resource(IngredientDetail, '/ingredient/<id>')

api.add_resource(StoreSectionList, '/store_section')
api.add_resource(StoreSectionDetail, '/store_section/<id>')
