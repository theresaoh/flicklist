import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_ECHO'] = True
project_dir = os.path.dirname(os.path.abspath(__file__)) # grab the current project directory
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "flicklist.db"))

db = SQLAlchemy(app)