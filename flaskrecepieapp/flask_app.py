import datetime

from flask import Flask,request,render_template,redirect,flash,session,url_for,abort

# ORM FOR creating models
# https: // auth0.com/blog/sqlalchemy-orm-tutorial-for -python-developers/
from flask_sqlalchemy import SQLAlchemy

# FOR PASSWORD HASHING
# https://www.okta.com/uk/blog/2019/03/what-are-salted-passwords-and-password-hashing/
from flask_bcrypt import Bcrypt



app = Flask(__name__)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.db"
# Secret key to enable the use of session
app.secret_key = 'Secret key'
# initialize the app with the extension
db.init_app(app)


##MODELS : 

# Define user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Email is defined unique for all users
    email = db.Column(db.String, unique=True, nullable=False)
    mobile = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    # One to many relationship with Recipe 
    recipes = db.relationship('Recipe', backref='user', lazy=True)
    # LAST updated date and time
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.now)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Many to one realtionship with user via foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable = True) # Food / Snack
    description = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    # LAST updated date and time
    updated_at = db.Column(
        db.DateTime, onupdate=datetime.datetime.now)


## CREATE TABLES FOR MODELS IF NOT ALREADY CREATED
with app.app_context():
    db.create_all()

## helper functions

# Generate hash value for plain text password
def hash_password(password):# takes plaintext password as parameter
    return bcrypt.generate_password_hash(password).decode('utf-8')

# Compare password hash and plaintext password and verify whether they match
def verify_password(password_hash,password):
    return bcrypt.check_password_hash(password_hash, password)

# check if user is logged in using session variable
def is_user_logged_in():
    return 'isloggedin' in session and session['isloggedin'] == True

# redirect user to login page if not loggedin
# or login has expired
def user_not_loggedin_redirect():
    return redirect(url_for('user_login'))

def get_current_user():
    if is_user_logged_in():
        # get user by primary key / id
        return db.session.get(User,session['userid'])
    return None



## Route handler methods

@app.route("/signup",methods=['GET','POST'])
def user_signup():
    # if user is loggedin then redirect to dashboard
    if is_user_logged_in():
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        # get form data from request.form
        form = request.form
        # create an instance of user from form data
        user = User(email=form['email'],
                    mobile=form['mobile'],
                    # save password hash instead of plaintext password
                    password=hash_password(form['password']),
                    first_name=form['first_name'],
                    last_name=form['last_name'],
                    gender=form['gender'])
        
        # TO catch the SQLIntegrity Error for duplicate email
        try:
            # add user to database
            db.session.add(user)
            # commit changes to the database
            db.session.commit()
            flash('Account created successfully !','success')
        except Exception as e:
            print(e)
            # catch exception ( Integrity Error ) for duplicate email
            # Flash error message to user
            flash('Email ID already exists','danger')
        
    return render_template("usersignup.html")

@app.route("/login", methods=['GET','POST'])
def user_login():
    # if user is loggedin then redirect to dashboard
    if is_user_logged_in():
        return redirect(url_for('user_dashboard'))

    if request.method=='POST':
        form = request.form
        try:
            user = User.query.filter_by(email=form['email']).first()
            if verify_password(user.password,form['password']):
                # if password verified
                # login user 
                # create new session
                # set loggedin = True
                session['isloggedin']=True
                # set current session user
                session['userid']=user.id
                flash('Login successful !','success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('Incorrect Password')
        except Exception as e:
          print(e)
          flash('User does not exist','danger')
          
    return render_template("userlogin.html")
   

@app.route('/changepassword',methods=['GET','POST'])
def change_password():
    if is_user_logged_in():
        # fetch the current user from the database
        user = get_current_user()
        if request.method=='POST':
            # get form data
            form = request.form
            # verify current password
            if verify_password(user.password,form['password']):
                # if verified
                # then change password to new password
                user.password = hash_password(form['new_password'])
                # commit changes to the DB
                db.session.commit()
                flash('Password changed successfully !','success')
            else:
                flash('Current password is incorrect !','danger')
                
        return render_template('changepassword.html',user=user)#pass user data
    else:
        return user_not_loggedin_redirect()

@app.route('/logout')
def user_logout():
    # remove 'isloggedin' from session
    session.pop('isloggedin', None)
    # remove 'userid' from session
    session.pop('userid', None)
    # redirect to login page
    return user_not_loggedin_redirect()


@app.route('/profile',methods=['GET','POST'])
def user_profile():
    if is_user_logged_in():
        # fetch current user from db
        user = get_current_user()
        if request.method == 'POST':
            form = request.form
            
            #update user profile details received through form
            user.email = form['email']
            user.mobile = form['mobile']
            user.first_name = form['first_name']
            user.last_name = form['last_name']
            user.gender  =form['gender']
            
            # to handle integrity error caused by duplicate email
            try:
              db.session.commit()
            except Exception:
              flash('Email belongs to other user !')
        # pass user details to the template
        return render_template('userprofile.html',user=user)
    else:
        return user_not_loggedin_redirect()


@app.route("/create",methods=['GET','POST'])
def create_recipe():
    if is_user_logged_in():
        if request.method == 'POST':
            user = get_current_user()
            form = request.form
            # create new recipe instance from form data
            recipe = Recipe(
                            user_id = user.id , # set user_id to current user_id
                            name = form['name'],
                            category = form['category'],
                            description = form['description'],
                            ingredients = form['ingredients'],
                            instructions = form['instructions']
                            )     
            
            db.session.add(recipe)
            db.session.commit()
            
            # get recipe image file from form
            image = request.files['image']
            
            # save the image under the specific folder
            image.save(f'static/images/recipes/{recipe.id}.jpg')
            
            flash('Recipie created successfully !','success')
            
        return render_template('createrecipe.html')
    else:
        return user_not_loggedin_redirect()

@app.route('/dashboard')
def user_dashboard():
    if is_user_logged_in():
        user = get_current_user()
        # get all recipes owned / created by the current user
        # order by updated_at in descending order as a list
        recipes = Recipe.query.filter_by(user_id=user.id).order_by(Recipe.updated_at.desc())
        return render_template('userdashboard.html',recipes=recipes)
    else:
        return user_not_loggedin_redirect()

@app.route('/recipes/<int:recipe_id>/edit',methods=['GET','POST'])
# pass recipe_id as parameter
def edit_recipe(recipe_id):
    if is_user_logged_in():
        user = get_current_user()
        # check if recipe exists in database
        recipe = db.session.get(Recipe,recipe_id)
        if recipe:
            # if recipe exists in database
            # if the recipe is created by the current user
            # the allow the user to update
            # otherwise throw error
            if recipe.user_id == user.id:
                if request.method=='POST':
                    form = request.form
                    recipe.name = form['name']
                    recipe.category = form['category']
                    recipe.description = form['description']
                    recipe.ingredients = form['ingredients']
                    recipe.instructions = form['instructions']
                    
                    db.session.commit()
                    
                    if request.files['image']:
                        image = request.files['image']

                        image.save(f'static/images/recipes/{recipe.id}.jpg')

                        flash('Recipie updated successfully !', 'success')
            else:
                abort(403)# 403 forbidden to edit the recipe
        else:
            abort(404)# 404 recipe not found
        return render_template('editrecipe.html',recipe=recipe)
    else:
        return user_not_loggedin_redirect()
    

@app.route('/recipes/<int:recipe_id>/delete')
def delete_recipe(recipe_id):
    if is_user_logged_in():
        user = get_current_user()
        # check if recipe exists in database
        recipe = db.session.get(Recipe,recipe_id)
        
        if recipe:
            # if recipe exists in database
            # if the recipe is created by the current user
            # the allow the user to update
            # otherwise throw error
            if recipe.user_id == user.id:
                # delete from database
                db.session.delete(recipe)
                # commit changes to db
                db.session.commit()
                
                return redirect(url_for('user_dashboard'))
            
            else:
                abort(403)  # 403 forbidden to edit the recipe
        else:
            abort(404)# 404 recipe not found
    else:
        return user_not_loggedin_redirect()


@app.route("/")
def home():
    recipes = Recipe.query.all()
    return render_template("home.html",recipes=recipes)

if __name__ == "__main__":
    app.run(debug=True)