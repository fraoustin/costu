from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user
from auth import checkAdmin
from werkzeug.utils import secure_filename
import os
import datetime
import unidecode
import random

from db import db
from db.models import ParamApp

PARAMS = ['titlehome', 'bodyhome', 'bannerhome', 'contacthome']


@login_required
@checkAdmin()
def view():
    params = {}
    for param in PARAMS:
        params[param] = ParamApp.getValue(param)
    return render_template('homepage.html', **params)


@login_required
@checkAdmin()
def update():
    for param in PARAMS:
        print(param)
        paramregister = ParamApp.get(param)
        paramregister.value = request.form.get(param,'')
        paramregister.save()

    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        pathfile = os.path.join(current_app.config['APP_IMG'], unidecode.unidecode(filename))
        file.save(pathfile)
    return redirect(url_for('homepage.view'))
    

class HomePage(Blueprint):
    def __init__(self, name='homepage', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/homepage', 'view', view, methods=['GET'])
        self.add_url_rule('/homepage', 'update_homepage', update, methods=['POST'])
        
    def init_db(self):
        for param in PARAMS:
            if ParamApp.get(param) is None:
                db.session.add(ParamApp(key=param, value=''))
                db.session.commit()
                current_app.logger.info("create homepage parameter register %s" % param)

    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init homepage on register is failed")