from app import db

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


class Menu(db.Model):
    __tablename__ = 'menu'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    dishes = db.relationship('Dish', secondary='menu_dishes', passive_deletes=True)


class MenuDish(db.Model):
    __tablename__ = 'menu_dishes'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    menu_id = db.Column(db.ForeignKey('menu.id'))
    dish_id = db.Column(db.ForeignKey('dish.id'))
    portion = db.Column(db.Integer)

    menu = db.relationship('Menu', primaryjoin='MenuDish.menu_id == Menu.id', backref='menu_dishes')
    dish = db.relationship('Dish', primaryjoin='MenuDish.dish_id == Dish.id')


class Dish(db.Model):
    __tablename__ = 'dish'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    portion = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    all_time = db.Column(db.Integer)

    categories = db.relationship('DCategory', secondary=t_dish_categories, passive_deletes=True,
                                 backref=db.backref('Dish', lazy='dynamic'))


class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    dish_id = db.Column(db.ForeignKey('dish.id'))
    foodstuff_id = db.Column(db.ForeignKey('foodstuff.id'))
    unit_id = db.Column(db.ForeignKey('d_unit.id'))
    amount = db.Column(db.Float(53))
    pre_pack_type_id = db.Column(db.ForeignKey('d_pre_pack_type.id'))
    stage_id = db.Column(db.ForeignKey('d_stage.id'))

    alternatives = db.relationship('Foodstuff', secondary=t_ingredient_alternatives, passive_deletes=True)
    dish = db.relationship('Dish', primaryjoin='Ingredient.dish_id == Dish.id', backref='ingredients')
    foodstuff = db.relationship('Foodstuff', primaryjoin='Ingredient.foodstuff_id == Foodstuff.id')

    pre_pack_type = db.relationship('DPrePackType', primaryjoin='Ingredient.pre_pack_type_id == DPrePackType.id')
    stage = db.relationship('DStage', primaryjoin='Ingredient.stage_id == DStage.id')
    unit = db.relationship('DUnit', primaryjoin='Ingredient.unit_id == DUnit.id')


class Foodstuff(db.Model):
    __tablename__ = 'foodstuff'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)
    store_section_id = db.Column(db.ForeignKey('d_store_section.id'))

    store_section = db.relationship('DStoreSection', primaryjoin='Foodstuff.store_section_id == DStoreSection.id',
                                    backref='foodstuff')


class DCategory(db.Model):
    __tablename__ = 'd_category'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)

    dishes = db.relationship('Dish', secondary='dish_categories', backref='d_category')


class DPrePackType(db.Model):
    __tablename__ = 'd_pre_pack_type'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)


class DStage(db.Model):
    __tablename__ = 'd_stage'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)


class DStoreSection(db.Model):
    __tablename__ = 'd_store_section'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)


class DUnit(db.Model):
    __tablename__ = 'd_unit'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text)
