from app import db


class DCategory(db.Model):
    __tablename__ = 'd_category'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    dishes = db.relationship('Dish', secondary='dish_categories', backref='d_category')

    def __str__(self):
        return self.name

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class DPrePackType(db.Model):
    __tablename__ = 'd_pre_pack_type'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class DStage(db.Model):
    __tablename__ = 'd_stage'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class DStoreSection(db.Model):
    __tablename__ = 'd_store_section'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class DUnit(db.Model):
    __tablename__ = 'd_unit'

    name = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Foodstuff(db.Model):
    __tablename__ = 'foodstuff'

    name = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    store_section_id = db.Column(db.ForeignKey('d_store_section.id'))

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


t_dish_categories = db.Table(
    'dish_categories',
    db.Column('category_id', db.ForeignKey('d_category.id')),
    db.Column('dish_id', db.ForeignKey('dish.id'))
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
    dish_id = db.Column(db.ForeignKey('dish.id'))
    menu = db.relationship('Menu', primaryjoin='MenuDish.menu_id == Menu.id', backref='menu_dishes')
    dish = db.relationship('Dish', primaryjoin='MenuDish.dish_id == Dish.id')
    portion = db.Column(db.Integer, server_default=db.FetchedValue())

    def as_json(self):
        return {
            'id': self.id,
            'dish_id': self.dish_id,
            'portion': self.portion
        }


class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)
    dishes = db.relationship('Dish', secondary='menu_dishes', passive_deletes=True)

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'dishes': self.dishes
        }


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    dish_id = db.Column(db.ForeignKey('dish.id'))
    foodstuff_id = db.Column(db.ForeignKey('foodstuff.id'))
    unit_id = db.Column(db.ForeignKey('d_unit.id'))
    amount = db.Column(db.Float(53))
    pre_pack_type_id = db.Column(db.ForeignKey('d_pre_pack_type.id'))
    stage_id = db.Column(db.ForeignKey('d_stage.id'))

    dish = db.relationship('Dish', primaryjoin='Ingredient.dish_id == Dish.id',
                           backref='ingredients')
    foodstuff = db.relationship('Foodstuff', primaryjoin='Ingredient.foodstuff_id == Foodstuff.id')
    ingredient_alternatives = db.relationship('Foodstuff', secondary=t_ingredient_alternatives, passive_deletes=True)

    prepack_type = db.relationship('DPrePackType', primaryjoin='Ingredient.pre_pack_type_id == DPrePackType.id')
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


class Dish(db.Model):
    __tablename__ = 'dish'

    name = db.Column(db.Text)
    description = db.Column(db.Text)
    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    portion = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    all_time = db.Column(db.Integer)
    categories = db.relationship('DCategory', secondary=t_dish_categories, passive_deletes=True,
                                 backref=db.backref('Dish', lazy='dynamic'))
