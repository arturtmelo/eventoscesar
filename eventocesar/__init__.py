import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = '29cecf8afd6176f06bb3f55472d490d1'

# Criar diretório 
db_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'eventocesar')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Caminho absoluto-SQLAlchemy 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.path.join(db_dir, 'comunidade.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
WTF_CSRF_ENABLED = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from eventocesar import routes

if __name__ == '__main__':
    app.run(debug=True)
