from flask_login import current_user
from flask import current_app
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
import hashlib


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    lastconnection = db.Column(db.Date, nullable=True)
    isadmin = db.Column(db.Boolean, default=False, nullable=False)
    gravatar = db.Column(db.Boolean, default=False, nullable=False)
    apikey = db.Column(db.String, nullable=True)
    token = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)
    group = db.Column(db.String, nullable=True)

    def __setattr__(self, name, value):
        if name in ('isadmin','gravatar') and type(value) == str:
            if value in ['true','True']:
                value = True
            else:
                value = False
        if name == 'password':
            value = generate_password_hash(value)
        db.Model.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if name in ('lastconnection'):
            if db.Model.__getattribute__(self, name) != None:
                return db.Model.__getattribute__(self, name).strftime('%d/%m/%Y')
            else:
                return ""
        if name == 'urlgravatar':
            return "https://www.gravatar.com/avatar/" + hashlib.md5(self.email.encode().lower()).hexdigest()
        if name not in ('id') and db.Model.__getattribute__(self, name) == None:
            return ""
        return db.Model.__getattribute__(self, name)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the id to satisfy Flask-Login's requirements."""
        return self.id

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
    
    def is_authenticated(self):
        return True
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def has_authorization(self, modul, key):
        if self.isadmin is True:
            return True
        authorizations = Authorization.get(self.group)
        for authorization in authorizations:
            if authorization.modul == modul and authorization.key == key:
                return True
        return False


class GroupOfAuthorization(db.Model):
    __tablename__ = 'groupofauthorization'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def clean_authorization(self):
        for auth in Authorization.query.filter_by(idgroup=self.id).all():
            auth.remove()

    def add_authorisation(self, modul, key):
        auth = Authorization()
        auth.idgroup = self.id
        auth.modul = modul
        auth.key = key
        auth.save()

    @property
    def authorizations(self):
        return Authorization.query.filter_by(idgroup=self.id).all()


class Authorization(db.Model):
    __tablename__ = 'authorization'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idgroup = db.Column(db.Integer, nullable=False)
    modul = db.Column(db.String, nullable=False)
    key = db.Column(db.String, nullable=False)

    @classmethod
    def get(cls, idgroup):
        try:
            return cls.query.filter_by(idgroup=idgroup).all()
        except Exception:
            return None

    

class Param(db.Model):
    __tablename__ = 'param'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String, nullable=False)
    module = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=True)

    @classmethod
    def get(cls, module, key):
        try:
            return cls.query.filter_by(key=key).first()
        except:
            return None

    @classmethod
    def getValue(cls, module, key, default=""):
        try:
            return cls.query.filter_by(key=key, module=module).first().value
        except:
            return default

class ParamApp(Param):
    __tablename__ = 'param'

    @classmethod
    def get(cls, key=None):
        if key == None:
            return Param.query.filter(module='app').all()
        return Param.get('app', key)

    @classmethod
    def getValue(cls, key, default=""):
        return Param.getValue('app', key, default)

    def __setattr__(self, name, value):    
        db.Model.__setattr__(self, name, value)
        db.Model.__setattr__(self, 'module', 'app')


class Suit(db.Model):
    __tablename__ = 'custom'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    portant = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)
    epoque = db.Column(db.String, nullable=True)
    gender = db.Column(db.String, nullable=True)
    size = db.Column(db.String, nullable=True)
    color = db.Column(db.String, nullable=True)
    state = db.Column(db.String, nullable=True)
    dispo = db.Column(db.String, nullable=True)
    bas = db.Column(db.String, nullable=True)
    haut = db.Column(db.String, nullable=True)
    robe = db.Column(db.String, nullable=True)
    ensemble = db.Column(db.String, nullable=True)
    accessoire = db.Column(db.String, nullable=True)
    lastmodifiedby = db.Column(db.String, nullable=True)
    lastmodified = db.Column(db.DateTime, nullable=True)

    def __setattr__(self, name, value):
        if type(value) == str and len(value) == 0:
            value = None
        db.Model.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name == 'pictures':
            return Picture.query.filter_by(idsuit=self.id).all()
        return db.Model.__getattr__(self, name)

    def __getattribute__(self, name):
        if name not in ('id') and db.Model.__getattribute__(self, name) == None:
            return ""
        return db.Model.__getattribute__(self, name)
    
    def save(self):
        try:
            self.lastmodifiedby = current_user.name
        except Exception as err:
            self.lastmodifiedby = 'external'
        self.lastmodified = datetime.datetime.now()
        db.Model.save(self)
    
    def add_picture(self, png):
        picture = Picture(idsuit=self.id, 
            png=png)
        picture.save()
        return picture
    
    def remove(self):
        for picture in self.pictures:
            picture.remove()
        return db.Model.remove(self)
    
    @property
    def idformat(self):
        fmt = '{:0>' + ParamApp.getValue('formatid', '4') + '}'
        return fmt.format(self.id)
            



class Picture(db.Model):
    __tablename__ = 'picture'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idsuit = db.Column(db.Integer, nullable=True)
    png = db.Column(db.String, nullable=False)
    lastmodifiedby = db.Column(db.String, nullable=True)
    lastmodified = db.Column(db.DateTime, nullable=True)

    def __setattr__(self, name, value):
        if type(value) == str and len(value) == 0:
            value = None
        db.Model.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if name == 'png':
            if self.id is not None and os.path.isfile(os.path.join(current_app.config['APP_IMG'], "%s.png" % str(self.id))):
                with open(os.path.join(current_app.config['APP_IMG'], "%s.png" % str(self.id)), "r") as filepng:
                    return filepng.read()
        if name not in ('id') and db.Model.__getattribute__(self, name) == None:
            return ""
        return db.Model.__getattribute__(self, name)
    
    def save(self):
        try:
            self.lastmodifiedby = current_user.name
        except Exception as err:
            self.lastmodifiedby = 'external'
        self.lastmodified = datetime.datetime.now()
        dataimg = self.png
        self.png = "in file"
        db.Model.save(self)
        with open(os.path.join(current_app.config['APP_IMG'], "%s.png" % str(self.id)), "w") as filepng:
            filepng.write(dataimg)
    
    def remove(self):
        if self.id is not None and os.path.isfile(os.path.join(current_app.config['APP_IMG'], "%s.png" % str(self.id))):
            os.remove(os.path.join(current_app.config['APP_IMG'], "%s.png" % str(self.id)))
        return db.Model.remove(self)
    

    

class Partner(db.Model):
    __tablename__ = 'partner'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=True)
    img = db.Column(db.String, nullable=True)
    actif = db.Column(db.Boolean, default=False, nullable=False)

    def __getattribute__(self, name):
        if name not in ('id') and db.Model.__getattribute__(self, name) == None:
            return ""
        return db.Model.__getattribute__(self, name)