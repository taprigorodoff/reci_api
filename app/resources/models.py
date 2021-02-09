from app import db


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


class Foodstuff(db.Model):
    __tablename__ = 'foodstuff'

    name = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    store_section_id = db.Column(db.ForeignKey('d_store_sections.id'))

    store_section = db.relationship('DStoreSection', primaryjoin='Foodstuff.store_section_id == DStoreSection.id',
                                    backref='foodstuff')

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'store_section':
                {
                    'id': self.store_section.id,
                    'name': self.store_section.name
                }
        }


t_recipe_categories = db.Table(
    'recipe_categories',
    db.Column('category_id', db.ForeignKey('d_categories.id')),
    db.Column('recipe_id', db.ForeignKey('recipes.id'))
)

t_ingredient_alternatives = db.Table(
    'ingredient_alternatives',
    db.Column('ingredient_id', db.ForeignKey('ingredient.id')),
    db.Column('foodstuff_id', db.ForeignKey('foodstuff.id'))
)


class MenuDish(db.Model):
    __tablename__ = 'menu_dishes'
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    menu_id = db.Column(db.ForeignKey('menu.id'))
    recipe_id = db.Column(db.ForeignKey('recipes.id'))
    menu = db.relationship('Menu', primaryjoin='MenuDish.menu_id == Menu.id', backref='menu_dishes')
    recipe = db.relationship('Recipe', primaryjoin='MenuDish.recipe_id == Recipe.id')
    portion = db.Column(db.Integer, server_default=db.FetchedValue())

    def as_json(self):
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'portion': self.portion
        }


class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)
    dishes = db.relationship('Recipe', secondary='menu_dishes', passive_deletes=True)

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'dishes': self.dishes
        }


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    recipe_id = db.Column(db.ForeignKey('recipes.id'))
    foodstuff_id = db.Column(db.ForeignKey('foodstuff.id'))
    unit_id = db.Column(db.ForeignKey('d_units.id'))
    amount = db.Column(db.Float(53))
    prepack_type_id = db.Column(db.ForeignKey('d_prepack_types.id'))
    stage_id = db.Column(db.ForeignKey('d_stages.id'))

    recipe = db.relationship('Recipe', primaryjoin='Ingredient.recipe_id == Recipe.id',
                             backref='ingredients')
    foodstuff = db.relationship('Foodstuff', primaryjoin='Ingredient.foodstuff_id == Foodstuff.id')
    ingredient_alternatives = db.relationship('Foodstuff', secondary=t_ingredient_alternatives, passive_deletes=True)

    prepack_type = db.relationship('DPrepackType', primaryjoin='Ingredient.prepack_type_id == DPrepackType.id')
    stage = db.relationship('DStage', primaryjoin='Ingredient.stage_id == DStage.id')
    unit = db.relationship('DUnit', primaryjoin='Ingredient.unit_id == DUnit.id')

    def as_json(self):
        result = {
            'id': self.id,
            'foodstuff': self.foodstuff.name,
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
                alternatives.append(ai.name)
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
    categories = db.relationship('DCategory', secondary=t_recipe_categories, passive_deletes=True,
                                 backref=db.backref('Recipe', lazy='dynamic'))

    def as_full_json(self):
        recipe_ingredients = {}
        pre_pack = {}

        for ob in self.ingredients:
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
