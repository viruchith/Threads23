from flask import Flask,render_template,request,abort,redirect
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
class ShortRedirect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # ALIAS given by user for the given url
    alias = db.Column(db.String,unique=True,nullable=False)
    # GIVEN URL TO REDIRECT TO
    url = db.Column(db.String,nullable=False)
    


#CREATE TABLES FOR  MODELS
with app.app_context():
    db.create_all()


@app.route("/",methods=['GET','POST'])
def create():
    data = {
        "host":"localhost:5000",# change appropriately
        #initially set data as empty
        "url":"",
        "alias":""} # initialize with empty strings
    error = {}
    # if form is submitted on the client side then
    if request.method=='POST':
        
        data['alias'] = request.form['alias']
        data['url'] = request.form['url']
        # Create an instance of the ShortRedirect by specifying the fields via constructor
        short_redirect = ShortRedirect(url=request.form['url'],alias=request.form['alias'])
        db.session.add(short_redirect) # insert the short_redirect into the db table
        try:
            db.session.commit()  # commit the changes done to the db
        except Exception:
          print('Alias already exists !')
          error['message'] = 'Alias taken ! Please choose another !'
          
    return render_template("index.html",data=data,error=error)

@app.route("/<alias>")
def alias_redirect(alias):
    try:
        #find the short redirect by alias
        short_redirect = ShortRedirect.query.filter_by(alias=alias).one()
    except Exception:
        #if alias does not exist the throw 404 not found
      print('Alias does not exist !')
      abort(404)
    return redirect(short_redirect.url,code=302)

@app.route("/hello")
def hello_world():
    return "<p>Hello, World!</p>"






if __name__=="__main__":
    app.run("0.0.0.0",debug=True)
