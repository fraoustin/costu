from flask import Blueprint, flash, request, render_template, redirect, url_for, current_app, send_from_directory
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import datetime
from auth import checkAdmin
import unidecode

from werkzeug.utils import secure_filename
import os

from db import db
from db.models import Partner

getBool ={'on': True, 'off': False}

@login_required
def view(id):
    try:
        partner = Partner.get(id=id)
        if partner is not None:
            return render_template('partnership.html', partner=partner)
        else:
            raise('partner not found')
    except:
        flash('Not found partner', 'warning')
        return redirect(url_for('partnership.partnerships'))
        
@login_required
def new():
    return render_template('partnership.html', partner=Partner())


@login_required
def create():
    partner = Partner(name=request.form['name'],
        url=request.form['url'],
        img=request.form['img'],
        actif=getBool.get(request.form.get('actif','off'),False))
    partner.save()
    flash('Partner "%s" is created' % partner.name, 'success')
    return redirect(url_for('partnership.view_partnership', id=partner.id))


@login_required
def update(id):
    partner = Partner.get(id=id)
    if partner is not None:
        partner.name = request.form['name']
        partner.url = request.form['url']
        partner.img = request.form['img']
        partner.actif = getBool.get(request.form.get('actif','off'),False)
        partner.save()
        flash('Partner "%s" is saved' % partner.name, 'success')
        return redirect(url_for('partnership.view_partnership', id=partner.id))
    else:
        flash('Partner doesn\'t exist','error')
        return redirect(url_for('partnership.partnerships'))


@login_required
def delete(id):
    partner = Partner.get(id=id)
    if partner is not None:
        partner.remove()
        flash('partner "%s" is deleted' % id,'error')
    return redirect(url_for('partnership.partnerships'))


@login_required
def list():
    return render_template("partnerships.html", partners=Partner.all(sortby=Partner.id))


class PartnerShip(Blueprint):

    def __init__(self, name='partnership', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/partnership/<int:id>', 'view_partnership', view, methods=['GET'])
        self.add_url_rule('/partnership', 'new_partnership', new, methods=['GET'])
        self.add_url_rule('/partnership', 'create_partnership', create, methods=['POST'])
        self.add_url_rule('/partnership/<int:id>', 'update_partnership', update, methods=['POST'])
        self.add_url_rule('/delpartnership/<int:id>', 'delete_partnership', delete, methods=['POST'])
        self.add_url_rule('/partnerships', 'partnerships', list, methods=['GET'])

    def register(self, partnership, options, first_registration=False):
        try:
            Blueprint.register(self, partnership, options, first_registration)
        except:
            partnership.logger.error("init partnership on register is failed")
