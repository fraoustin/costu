import os, logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from db import db
from auth import Auth, login_required
from info import Info
from static import Static
from paramapplication import ParamApplication

toBoolean = {'true': True, 'false':False}

COSTU_PORT = int(os.environ.get('COSTU_PORT', '5000'))
COSTU_DEBUG = toBoolean.get(os.environ.get('COSTU_DEBUG', 'false'), False)
COSTU_HOST = os.environ.get('COSTU_HOST', '0.0.0.0')
COSTU_DIR = os.environ.get('COSTU_DIR', os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config["VERSION"] = "0.1.0"

app.config["APP_PORT"] = COSTU_PORT
app.config["APP_HOST"] = COSTU_HOST
app.config["APP_DEBUG"] = COSTU_DEBUG
app.config["APP_DIR"] = COSTU_DIR

# db SQLAlchemy
database_file = "sqlite:///{}".format(os.path.join(COSTU_DIR, "costu.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
# register Auth
app.register_blueprint(Auth(url_prefix="/"))
app.config['APP_NAME'] = os.environ.get('COSTU_NAME', 'COSTU')
app.config['APP_DESC'] = os.environ.get('COSTU_DESC', 'Inventaire de la costumerie')
# register Info
app.register_blueprint(Info(url_prefix="/"))
# register Static
COSTU_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
app.register_blueprint(Static(name="js", url_prefix="/javascripts/", path=os.path.join(COSTU_PATH, "javascripts")))
app.register_blueprint(Static(name="siimple", url_prefix="/siimple/", path=os.path.join(COSTU_PATH, "siimple")))
app.register_blueprint(Static(name="css", url_prefix="/css/", path=os.path.join(COSTU_PATH, "css")))
# register ParamApplication
app.register_blueprint(ParamApplication(url_prefix="/"))

# register COSTU
from suits import Suits
app.register_blueprint(Suits(url_prefix="/"))

# register SEARCH
from search import Search
app.register_blueprint(Search(url_prefix="/"))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')


if __name__ == "__main__":
    db.init_app(app)
    with app.app_context():
        db.create_all()
    with app.app_context():
        for bp in app.blueprints:
            if 'init_db' in dir(app.blueprints[bp]):
                app.blueprints[bp].init_db()
    app.logger.setLevel(logging.DEBUG)
    app.run(host=COSTU_HOST, port=COSTU_PORT, debug=COSTU_DEBUG)