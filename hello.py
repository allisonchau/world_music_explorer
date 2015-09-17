import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://home/worldmusicexplorer'
#     'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


db = SQLAlchemy(app)



# postgresql://username:password@hostname/database