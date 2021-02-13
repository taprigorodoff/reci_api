from flask import Flask
from flask_caching import Cache
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from config import Configuration

from flask_apispec.extension import FlaskApiSpec

app = Flask(__name__)
api = Api(app)
app.config.from_object(Configuration)

db = SQLAlchemy(app)
cache = Cache(app)
docs = FlaskApiSpec(app)

from resources.Dish import DishList, DishDetail, DishImg
from resources.Ingredient import IngredientList, IngredientDetail
from resources.Foodstuff import FoodstuffList, FoodstuffDetail
from resources.Dictionary import StoreSectionList, StoreSectionDetail, \
                                 UnitList, UnitDetail, \
                                 StageList, StageDetail,\
                                 CategoryList, CategoryDetail, \
                                 PrePackTypeList, PrePackTypeDetail
from resources.Menu import MenuList, MenuDetail
from resources.Menu import MenuDishList, MenuDishDetail
from resources.Menu import MenuShoppingList

api.add_resource(DishList, '/dish')
api.add_resource(DishDetail, '/dish/<id>')
api.add_resource(DishImg, '/dish/<id>/img')
api.add_resource(IngredientList, '/dish/<dish_id>/ingredient')
api.add_resource(IngredientDetail, '/dish/<dish_id>/ingredient/<id>')

api.add_resource(FoodstuffList, '/foodstuff')
api.add_resource(FoodstuffDetail, '/foodstuff/<id>')

api.add_resource(StoreSectionList, '/store_section')
api.add_resource(StoreSectionDetail, '/store_section/<id>')
api.add_resource(UnitList, '/unit')
api.add_resource(UnitDetail, '/unit/<id>')
api.add_resource(StageList, '/stage')
api.add_resource(StageDetail, '/stage/<id>')
api.add_resource(CategoryList, '/category')
api.add_resource(CategoryDetail, '/category/<id>')
api.add_resource(PrePackTypeList, '/pre_pack_type')
api.add_resource(PrePackTypeDetail, '/pre_pack_type/<id>')

api.add_resource(MenuList, '/menu')
api.add_resource(MenuDetail, '/menu/<id>')

api.add_resource(MenuDishList, '/menu/<menu_id>/dish')
api.add_resource(MenuDishDetail, '/menu/<menu_id>/dish/<id>')

api.add_resource(MenuShoppingList, '/menu/<menu_id>/shopping')

docs.register(DishList)
docs.register(DishDetail)
docs.register(IngredientList)
docs.register(IngredientDetail)
docs.register(DishImg)

docs.register(FoodstuffList)
docs.register(FoodstuffDetail)

docs.register(StoreSectionList)
docs.register(StoreSectionDetail)
docs.register(UnitList)
docs.register(UnitDetail)
docs.register(StageList)
docs.register(StageDetail)
docs.register(CategoryList)
docs.register(CategoryDetail)
docs.register(PrePackTypeList)
docs.register(PrePackTypeDetail)

docs.register(MenuList)
docs.register(MenuDetail)
docs.register(MenuDishList)
docs.register(MenuDishDetail)
docs.register(MenuShoppingList)
