from flask import request
from . import app, db 
from .models import User, Recipe, Comment, Ingredient
from. auth import basic_auth, token_auth


@app.route('/users', methods = ['POST'])
def create_user():
    if not request.is_json:
        return {"error": 'Your content-type must be application/json'}, 400
    data=request.json

    
    required_fields = ['firstName', 'lastName', 'username','email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f" {','.join(missing_fields)} must be in the request body"}, 400
    

    first_name = data.get('firstName')
    last_name= data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    check_users=db.session.execute(db.select(User).where((User.username == username) | (User.email == email))).scalars().all()
    if check_users:
        return {'error': 'A user with that username and/or email already exists'}, 400


    new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)


    return new_user.to_dict(), 201

@app.route('/token')
@basic_auth.login_required
def get_token():
    user=basic_auth.current_user()
    return user.get_token()

@app.route('/users/me')
@token_auth.login_required
def get_me():
    user = token_auth.current_user()
    return user.to_dict()

@app.route('/recipes')
def get_recipes():
    select_stmt = db.select(Recipe)
    recipes = db.session.execute(select_stmt).scalars().all()
    return [r.to_dict() for r in recipes]

@app.route('/recipes/<int:recipe_id>')
def get_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)
    if recipe:
        return recipe.to_dict()
    else:
        return {'error': f"Recipe with an ID of {recipe_id} does not exist"}, 404

@app.route('/recipes', methods=['POST'])
@token_auth.login_required
def create_recipe():
    if not request.is_json:
        return {'error': 'Your content-type must be applicaion/json'}
    data=request.json
    required_fields = ['name', 'description', 'cuisine', 'cookTime', "servings", 'ingredients', 'instructions']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {"error": f"{','.join(missing_fields)} must be in the request body"}, 400
    
    name = data.get('name')
    description = data.get('description')
    cuisine = data.get('cuisine')
    cookTime = data.get('cookTime')
    servings=data.get('servings')
    ingredients=data.get('ingredients')
    instructions=data.get('instructions')

    
    current_user=token_auth.current_user()

    new_recipe = Recipe(name=name, description=description, cuisine=cuisine, cookTime=cookTime, servings=servings, ingredients=ingredients, instructions=instructions, user_id=current_user.id)

    return new_recipe.to_dict(), 201

@app.route('/recipes/<int:recipe_id>', methods=['PUT'])
@token_auth.login_required
def edit_recipe(recipe_id):
    if not request.is_json:
        return {"error": "Your content-type must be application/json"}, 400
    recipe = db.session.get(Recipe, recipe_id)
    if recipe is None:
        return {"error": f"Recipe with id of {recipe_id} does not exist"}, 404
    current_user=token_auth.current_user()
    if current_user is not recipe.author:
        return {'error': "This is not your recipe. You do not ahve permission to edit"}, 403
    
    data=request.json

    recipe.update(**data)
    return recipe.to_dict()

@app.route('/recipes/<int:recipe_id>', methods=["DELETE"])
@token_auth.login_required
def delete_recipe(recipe_id):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return {'error': f'Recipe with {recipe_id} does not exist/ Please try again.'}, 404
    
    current_user=token_auth.current_user()
    if recipe.author is not current_user:
        return {'error':'You do not have permission to delete this recipe'}, 403
    
    recipe.delete()
    return {'success': f"'{recipe.name}' was successfully deleted"}, 200

@app.route('/recipes/<int:recipe_id>/comments', methods=['POST'])
@token_auth.login_required
def create_comment(recipe_id):
    if not request.is_json:
        return {"error": 'Your content type must be application/json'}, 400
    recipe=db.session.get(Recipe, recipe_id)
    if recipe is None:
        return {'error': f"Recipe {recipe_id} does not exist."}, 404
    
    data=request.json

    required_fields = ['body']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)

    if missing_fields:
        return {"error": f"{', '.join(missing_fields)} must be present in the request body"}, 400
    
    body = data.get('body')
    current_user = token_auth.current_user()
    new_comment = Comment(body=body, user_id = current_user.id, recipe_id =recipe.id)
    return new_comment.to_dict(), 201

@app.route('/recipes/<int:recipe_id>/comments/<int:comment_id>', methods = {'DELETE'})
@token_auth.login_required
def delete_comment(recipe_id, comment_id):
    recipe=db.session.get(Recipe, recipe_id)
    if recipe is None:
        return {"error": f"Recipe {recipe_id} does not exist."}, 404
    comment = db.session.get(Comment, comment_id)
    if comment is None:
        return {"comment": f"Comment {comment_id} does not exist."}, 404
    
    if comment.recipe_id != recipe.id:
        return {'error': f"Comment #{comment_id} is not associated with recipe #{recipe_id}"}, 400 
    
    current_user = token_auth.current_user()

    if comment.author is not current_user:
        return {'error': 'You do not have permission to delete this comment'}, 403
    
    comment.delete()
    return {"success": f"Comment {comment_id} was successfully deleted."}


@app.route('/recipes/<int:recipe_id>/ingredients', methods=['POST'])
@token_auth.login_required
def create_ingredient(recipe_id):
    if not request.is_json:
        return {'error': 'Your content-type must be applicaion/json'}
    recipe=db.session.get(Recipe, recipe_id)
    if recipe is None:
        return {'error': f"Recipe {recipe_id} does not exist."}, 404
    
    data=request.json

    required_fields = ['name', 'quantity', 'unit']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {"error": f"{','.join(missing_fields)} must be in the request body"}, 400
    
    name = data.get('name')
    quantity=data.get('quantity')
    unit = data.get('unit')
    
    current_user=token_auth.current_user()

    new_ingredient = Ingredient(name=name, quantity=quantity, unit=unit, recipe_id=recipe.id)

    return new_ingredient.to_dict(), 201

@app.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>')
def get_ingredient(ingredient_id):
    ingredient = db.session.get(Ingredient, ingredient_id)
    if ingredient:
        return ingredient.to_dict()
    else:
        return {'error': f"Ingredient with an ID of {ingredient_id} does not exist"}, 404

@app.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>', methods=['PUT'])
@token_auth.login_required
def edit_ingredient(ingredient_id):
    if not request.is_json:
        return {"error": "Your content-type must be application/json"}, 400
    ingredient = db.session.get(Ingredient, ingredient_id)
    if ingredient is None:
        return {"error": f"Ingredient with id of {ingredient_id} does not exist"}, 404
    current_user=token_auth.current_user()
    if current_user is not ingredient.recipe.author:
        return {'error': "This is not your recipe. You do not ahve permission to edit"}, 403
    
    data=request.json

    ingredient.update(**data)
    return ingredient.to_dict()

@app.route('/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>', methods=["DELETE"])
@token_auth.login_required
def delete_ingredient(ingredient_id):
    ingredient = db.session.get(Ingredient, ingredient_id)

    if ingredient is None:
        return {"error": f"Ingredient with id of {ingredient_id} does not exist"}, 404
    
    current_user=token_auth.current_user()
    if ingredient.recipe.author is not current_user:
        return {'error':'You do not have permission to delete this ingredient'}, 403
    
    ingredient.delete()
    return {'success': f"'{ingredient.name}' was successfully deleted"}, 200