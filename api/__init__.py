from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c8d575d8223c4864889d86951a4b2d7a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///locovotiv.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# run it!
CORS(app, supports_credentials=True)
from api import routes
