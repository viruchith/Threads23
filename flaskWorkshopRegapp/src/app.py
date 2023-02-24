from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.db"
# initialize the app with the extension
db.init_app(app)


# Models
class Registrant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String,nullable=False)
    last_name = db.Column(db.String,nullable=False)
    email = db.Column(db.String,nullable=False)
    mobile = db.Column(db.String,nullable=False)
    gender = db.Column(db.String,nullable=False)
    address = db.Column(db.String,nullable=False)
    workshop = db.Column(db.String,nullable=False)
    


#CREATE TABLES FOR  MODELS
with app.app_context():
    db.create_all()


#Handle incoming requests for Rregistrants data
@app.route("/",methods=['GET','POST'])
def register():
    # if form is submitted on the client side then
    if request.method=='POST':
        # Create an instance of the registrant by specifying the fields via constructor
        registrant = Registrant(first_name=request.form['first_name'],
                                    last_name=request.form['last_name'], 
                                    email=request.form['email'] , 
                                    mobile = request.form['mobile'],
                                    gender = request.form['gender'],
                                    address = request.form['address'],
                                    workshop = request.form['workshop'])
        
        db.session.add(registrant) # insert the registrant into the db table
        db.session.commit() # commit the changes done to the db
        
        profile_pic = request.files['profile_pic'] # get the profile pic file from the form
        profile_pic.save(f'src/static/images/profile/{registrant.id}.jpg')# save the pic to static/images/profile as jpg

        return "<h1>Registration Successful !</h1>"
    
    return render_template("registrationform.html")


@app.route("/registered",methods=['GET'])
def get_registered():
    registrants = Registrant.query.all()# get all registrant objects as list
    return render_template("registrantstable.html",registrants = registrants)# pass the registrants list to the template

@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"






if __name__=="__main__":
    app.run("0.0.0.0",debug=True)
