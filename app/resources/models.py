from flask_sqlalchemy import SQLAlchemy
import json
import base64

db = SQLAlchemy()


class DCategory(db.Model):
    __tablename__ = 'd_categories'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    recipes = db.relationship('Recipe', secondary='recipe_categories', backref='d_categories')

    def as_json(self):
        return self.name


class DPrepackType(db.Model):
    __tablename__ = 'd_prepack_types'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    def as_json(self):
        return self.name


class DStage(db.Model):
    __tablename__ = 'd_stages'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)


class DStoreSection(db.Model):
    __tablename__ = 'd_store_sections'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class DUnit(db.Model):
    __tablename__ = 'd_units'

    name = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())


class IngredientAlternative(db.Model):
    __tablename__ = 'ingredient_alternatives'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    recipe_ingredient_id = db.Column(db.ForeignKey('recipe_ingredients.id'))
    ingredient_id = db.Column(db.ForeignKey('ingredients.id'))

    ingredient = db.relationship('Ingredient', primaryjoin='IngredientAlternative.ingredient_id == Ingredient.id',
                                 backref='ingredient_alternatives')
    recipe_ingredient = db.relationship('RecipeIngredient',
                                        primaryjoin='IngredientAlternative.recipe_ingredient_id == RecipeIngredient.id',
                                        backref='ingredient_alternatives')


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    name = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    store_section_id = db.Column(db.ForeignKey('d_store_sections.id'))

    store_section = db.relationship('DStoreSection', primaryjoin='Ingredient.store_section_id == DStoreSection.id',
                                    backref='ingredients')

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'store_section': self.store_section.name
        }


t_recipe_categories = db.Table(
    'recipe_categories',
    db.Column('category_id', db.ForeignKey('d_categories.id')),
    db.Column('recipe_id', db.ForeignKey('recipes.id'))
)


class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'

    recipe_id = db.Column(db.ForeignKey('recipes.id'))
    ingredient_id = db.Column(db.ForeignKey('ingredients.id'))
    unit_id = db.Column(db.ForeignKey('d_units.id'))
    amount = db.Column(db.Float(53))
    required = db.Column(db.Boolean, server_default=db.FetchedValue())
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    prepack_type_id = db.Column(db.ForeignKey('d_prepack_types.id'))
    stage_id = db.Column(db.ForeignKey('d_stages.id'))
    recipe_as_ingredient_id = db.Column(db.ForeignKey('recipes.id'))

    ingredient = db.relationship('Ingredient', primaryjoin='RecipeIngredient.ingredient_id == Ingredient.id',
                                 backref='recipe_ingredients')
    prepack_type = db.relationship('DPrepackType', primaryjoin='RecipeIngredient.prepack_type_id == DPrepackType.id',
                                   backref='recipe_ingredients')
    recipe_as_ingredient = db.relationship('Recipe',
                                           primaryjoin='RecipeIngredient.recipe_as_ingredient_id == Recipe.id',
                                           backref='recipe_recipe_ingredients')
    recipe = db.relationship('Recipe', primaryjoin='RecipeIngredient.recipe_id == Recipe.id',
                             backref='recipe_recipe_ingredients_0')
    stage = db.relationship('DStage', primaryjoin='RecipeIngredient.stage_id == DStage.id',
                            backref='recipe_ingredients')
    unit = db.relationship('DUnit', primaryjoin='RecipeIngredient.unit_id == DUnit.id', backref='recipe_ingredients')

    def as_json(self):
        result = {
            'ingredient': self.ingredient.name,  # TODO может быть не ингредиент, а рецепт. ссылка?
            'amount': self.amount,
            'unit': self.unit.name
        }

        if self.stage:
            result.update({'stage': self.stage.name})
        else:
            result.update({'stage': 'other'})

        if self.prepack_type:
            result.update({'pre_pack': self.prepack_type.name})

        if self.ingredient_alternatives:
            alternatives = []
            for ai in self.ingredient_alternatives:
                alternatives.append(ai.ingredient.name)
            result.update({'alternatives': alternatives})

        return result


class Recipe(db.Model):
    __tablename__ = 'recipes'

    name = db.Column(db.Text)
    description = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    portion = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    all_time = db.Column(db.Integer)
    categories = db.relationship('DCategory', secondary=t_recipe_categories,
                                 backref=db.backref('Recipe', lazy='dynamic'))

    def as_full_json(self):
        recipe_ingredients = {}
        pre_pack = {}

        for ob in self.recipe_recipe_ingredients_0:
            ingredient = ob.as_json()

            stage_name = ingredient.pop('stage')
            pre_pack_name = ingredient.pop('pre_pack', None)

            tmp_ingredients = recipe_ingredients.get(stage_name, [])
            tmp_ingredients.append(ingredient)
            recipe_ingredients.update({stage_name: tmp_ingredients})

            if pre_pack_name:
                tmp_pre_pack = pre_pack.get(pre_pack_name, [])
                tmp_pre_pack.append(ingredient)
                pre_pack.update({pre_pack_name: tmp_pre_pack})

        return {
            'id': self.id,
            'name': self.name,
            'portion': self.portion,
            'cook_time': self.cook_time,
            'all_time': self.all_time,
            'description': self.description,
            'categories': [ob.as_json() for ob in self.categories],
            'recipe_ingredients': recipe_ingredients,
            'pre_pack': pre_pack,
            'img': {
                'url':
                    '/recipe/img/{}'.format(self.id)
            }
        }

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'portion': self.portion,
            'cook_time': self.cook_time,
            'all_time': self.all_time,
            'description': self.description,
            'categories': [ob.as_json() for ob in self.categories]
        }
