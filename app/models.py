from . import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email=db.Column(db.String, nullable=False, unique=True)
    username=db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created=db.Column(db.DateTime, nullable=False, default = lambda: datetime.now(timezone.utc))
    recipes = db.relationship('Recipe', back_populates='author')
    comments = db.relationship('Comment', back_populates='author')
    ingredients = db.relationship('Ingredient', back_populates = 'author')
    instructions = db.relationship('Instruction', back_populates = 'author')
    saves=db.relationship('Save', back_populates = 'author')
    token = db.Column(db.String, index=True, unique=True)
    token_expiration = db.Column(db.DateTime(timezone=True))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password'))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>" 
    
    def set_password(self, plaintext_password):
        self.password = generate_password_hash(plaintext_password)
        self.save()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username": self.username,
            "dateCreated": self.date_created
        }
    
    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return {"token": self.token, "tokenExpiration":self.token_expiration}
        self.token=secrets.token_hex(16)
        self.token_expiration = now + timedelta(hours=1)
        self.save()
        return {"token": self.token, "tokenExpiration":self.token_expiration}

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    description = db.Column(db.String)
    cuisine = db.Column(db.String, nullable = False)
    cookTime = db.Column(db.String, nullable=False)
    servings = db.Column(db.String)
    date_created = db.Column(db.DateTime, nullable = False, default= lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='recipes')
    comments = db.relationship('Comment', back_populates='recipe')
    ingredients=db.relationship('Ingredient', back_populates='recipe')
    instructions=db.relationship('Instruction', back_populates='recipe')
    saves=db.relationship('Save', back_populates='recipe')

    def __repr__(self):
        return f"<Recipe {self.id}|{self.name}>"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        saves = db.session.execute(db.select(Save).where((Save.recipe_id == self.id)))

        count=0
        for save in saves:
            count+=1

        return {
            "id":self.id,
            "name": self.name,
            "description": self.description,
            "cuisine": self.cuisine,
            "cookTime": self.cookTime,
            "servings": self.servings,
            "dateCreated": self.date_created,
            "user_id": self.user_id,
            'author': self.author.to_dict(),
            'comments': [comment.to_dict() for comment in self.comments],
            "saves": count
        }
    
    def update(self, **kwargs):
        allowed_fields = {'name', 'description', "cuisine", "cookTime", "servings"}

        for key,value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    date_created=db.Column(db.DateTime, nullable=False, default= lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable =False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable = False)
    recipe = db.relationship('Recipe', back_populates='comments')
    author = db.relationship('User', back_populates='comments')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Comment {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'dateCreated': self.date_created,
            'recipe_id': self.recipe_id,
            'user': self.author.to_dict()
        }

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable = False)
    unit = db.Column(db.String, nullable=False)
    recipe_id= db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe=db.relationship('Recipe', back_populates='ingredients')
    author = db.relationship('User', back_populates='ingredients')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Ingredient {self.id}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, **kwargs):
        allowed_fields = ['name', 'quantity', 'unit']

        for key,value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()

    def delete (self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            "recipe_id": self.recipe_id,
            "user_id": self.user_id
        }

class Instruction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stepNumber = db.Column(db.Integer, nullable=False)
    body = db.Column(db.String, nullable=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe = db.relationship('Recipe', back_populates = 'instructions')
    author = db.relationship('User', back_populates='instructions')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Instruction {self.id}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        allowed_fields = ['stepNumber', 'body']

        for key,value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()

    def delete (self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'stepNumber': self.stepNumber,
            'body': self.body,
            "recipe_id": self.recipe_id,
            "user_id": self.user_id
        }
    
class Save(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id= db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe=db.relationship('Recipe', back_populates='saves')
    author = db.relationship('User', back_populates='saves')    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Save id {self.id}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, **kwargs):
        allowed_fields = ['recipe_id', 'user_id']

        for key,value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()

    def delete (self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "user_id": self.user_id
        }