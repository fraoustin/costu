from flask import Blueprint, flash, request, render_template, redirect, url_for, current_app, send_from_directory
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import datetime
from auth import checkAdmin
import unidecode

from werkzeug.utils import secure_filename
import os

from db import db
from db.models import Suit, Picture
from db.models import ParamApp

getBool ={'on': True, 'off': False}

LISTOFVALUE = ['location', 'epoque', 'gender', 'size', 'color', 'state', 'dispo', 'bas', 'haut', 'robe', 'ensemble', 'accessoire', 'sizecamera', 'rotate']

def getlistofvalue():
    params = {}
    for param in LISTOFVALUE:
        params[param] = ParamApp.getValue(param).split(';')
    params['translate'] = int((max([ int(size) for size in ParamApp.getValue('sizecamera').split('x')]) - min([ int(size) for size in ParamApp.getValue('sizecamera').split('x')]))/2)
    return params


@login_required
def view(id):
    try:
        suit = Suit.get(id=id)
        if suit is not None:
            return render_template('suit.html', suit=suit, listofvalue=getlistofvalue())
        else:
            raise('suit not found')
    except:
        flash('Not found suit', 'warning')
        return redirect(url_for('suits'))
        
@login_required
@checkAdmin()
def new():
    return render_template('suit.html', suit=Suit(location=current_user.location), listofvalue=getlistofvalue())


@login_required
def create():
    suit = Suit(location=request.form['location'],
        portant=request.form['portant'],
        description=request.form['description'],
        epoque=request.form['epoque'],
        gender=request.form['gender'],
        size=request.form['size'],
        color=request.form['color'],
        state=request.form['state'],
        dispo=request.form['dispo'],
        bas=request.form['bas'],
        haut=request.form['haut'],
        robe=request.form['robe'],
        ensemble=request.form['ensemble'],
        accessoire=request.form['accessoire'])
    suit.save()
    for picture in [elt for elt in request.form if elt.startswith('picture-')]:
        picture = Picture(idsuit=suit.id, png=request.form[picture])
        picture.save()
    flash('Suit "%s" is created' % suit.id, 'success')
    return redirect(url_for('suit.view_suit', id=suit.id))


@login_required
def update(id):
    suit = Suit.get(id=id)
    if suit is not None:
        suit.location = request.form['location']
        suit.portant = request.form['portant']
        suit.description = request.form['description']
        suit.epoque = request.form['epoque']
        suit.gender = request.form['gender']
        suit.size = request.form['size']
        suit.color = request.form['color']
        suit.state = request.form['state']
        suit.dispo = request.form['dispo']
        suit.haut = request.form['haut']
        suit.bas = request.form['bas']
        suit.robe = request.form['robe']
        suit.ensemble = request.form['ensemble']
        suit.accessoire = request.form['accessoire']
        suit.save()
        for picture in suit.pictures:
            if picture.id not in [elt.split('-')[1] for elt in request.form if elt.startswith('picture-')]:
                picture.remove()
                print('remove oldpicture')
        for picture in [elt for elt in request.form if elt.startswith('picture-')]:
            id = picture.split('-')[1]
            if id not in [ elt.id for elt in suit.pictures]:
                newpicture = Picture(idsuit=suit.id, png=request.form[picture])
                newpicture.save()
                print('newpicture')
        flash('Suit "%s" is saved' % suit.id,'success')
        return redirect(url_for('suit.view_suit', id=suit.id))
    else:
        flash('Suit doesn\'t exist','error')
        return redirect(url_for('suit.suits'))


@login_required
def delete(id):
    suit = Suit.get(id=id)
    if suit is not None:
        suit.remove()
        flash('Suit "%s" is deleted' % id,'error')
    return redirect(url_for('suit.suits'))


@login_required
def list():
    return render_template("suits.html", suits=Suit.all(sortby=Suit.id))


class Suits(Blueprint):

    def __init__(self, name='suit', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/suit/<int:id>', 'view_suit', view, methods=['GET'])
        self.add_url_rule('/suit', 'new_suit', new, methods=['GET'])
        self.add_url_rule('/suit', 'create_suit', create, methods=['POST'])
        self.add_url_rule('/suit/<int:id>', 'update_suit', update, methods=['POST'])
        self.add_url_rule('/delsuit/<int:id>', 'delete_suit', delete, methods=['POST'])
        self.add_url_rule('/suits', 'suits', list, methods=['GET'])

    def register(self, suit, options, first_registration=False):
        try:
            Blueprint.register(self, suit, options, first_registration)
        except:
            suit.logger.error("init suit on register is failed")
