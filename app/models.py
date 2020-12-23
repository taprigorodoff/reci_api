from app import db
import json

recipe_categories = db.Table('recipe_categories',
                             db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id')),
                             db.Column('category_id', db.Integer, db.ForeignKey('d_categories.id'))
                             )


class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    portion = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    all_time = db.Column(db.Integer)

    def __init__(self, *args, **kwargs):
        super(Recipes, self).__init__(*args, **kwargs)

    categories = db.relationship('d_categories', secondary=recipe_categories,
                                 backref=db.backref('recipes', lazy='dynamic'))

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'categories': [ob.as_json() for ob in self.categories]
        }


class d_categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(d_categories, self).__init__(*args, **kwargs)

    def as_json(self):
        return {
            'name': self.name
        }
