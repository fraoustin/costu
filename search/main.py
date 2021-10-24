from flask import Blueprint, render_template, current_app, request

from db import db
from db.models import Suit, Picture
from db.models import ParamApp

__version__ = '0.1.0'

LISTOFVALUE = ['location', 'epoque', 'gender', 'size', 'color', 'state', 'dispo', 'haut', 'bas', 'robe', 'ensemble', 'accessoire', 'sizecamera', 'rotate', 'sizepreview']

def onlyFound(suit):
    if suit.score > 0:
        return True
    return False

def del_accent(ligne):
        accents = { 'a': ['à', 'ã', 'á', 'â'],
                    'e': ['é', 'è', 'ê', 'ë'],
                    'i': ['î', 'ï'],
                    'u': ['ù', 'ü', 'û'],
                    'o': ['ô', 'ö'] }
        for char in accents:
            for accented_char in accents[char]:
                ligne = ligne.replace(accented_char, char)
        return ligne.lower()

class SuitSort():

    def __init__(self, suit, search, elts):
        self.suit = suit
        self.score = 0
        self.txt = del_accent(' '.join([getattr(suit, elt) for elt in elts]))
        for word in search.split(' '):
            if del_accent(word) in self.txt:
                self.score = self.score + 1

    def __getattribute__(self, name):
        if name in  ['score', 'suit', 'txt']:
            return super(SuitSort, self).__getattribute__(name)
        return self.suit.__getattribute__(name)
        

    def __lt__(self, other):
        return self.score < other.score

    def __le__(self, other):
        return self.score <= other.score

    def __eq__(self, other):
        return self.score == other.score

    def __ne__(self, other):
        return self.score != other.score

    def __gt__(self, other):
        return self.score > other.score

    def __ge__(self, other):
        return self.score >= other.score


def getlistofvalue():
    params = {}
    for param in LISTOFVALUE:
        params[param] = ParamApp.getValue(param).split(';')
    params['translate'] = int((max([ int(size) for size in ParamApp.getValue('sizecamera').split('x')]) - min([ int(size) for size in ParamApp.getValue('sizecamera').split('x')]))/2)
    params['translatepreview'] = int((max([ int(size) for size in ParamApp.getValue('sizepreview').split('x')]) - min([ int(size) for size in ParamApp.getValue('sizepreview').split('x')]))/2)
    return params

def search():
    return render_template('search.html', 
        listofvalue=getlistofvalue(),
        suits=[],
        location = request.form.get('location',''),
        gender = request.form.get('gender',''),
        element = request.form.get('elt',''),
        size = request.form.get('size',''),
        epoque = request.form.get('epoque',''),
        state = request.form.get('state',''),
        color = request.form.get('color',''),
        dispo = request.form.get('dispo',''),
        description = request.form.get('description',''), 
        titlehome=ParamApp.getValue('titlehome'), 
        bannerhome=ParamApp.getValue('bannerhome')
        )

def searchsuits():
    if request.form.get('update','no') == 'no':
        kw = { key : request.form[key] for  key in request.form if request.form.get(key,'') != '' and key not in ['update', 'description']}
        suits = Suit.query.filter_by(**kw).all()
        if request.form.get('description','') != '':
            elts = [ elt for elt in request.form if elt != 'update' ]
            suitsorts = [ SuitSort(suit, request.form.get('description',''), elts) for suit in suits]
            suitsorts.sort(reverse=True)
            suits = [suitsort.suit for suitsort in filter(onlyFound, suitsorts)]            
    else:
        suits = []
    return render_template('search.html', 
        listofvalue=getlistofvalue(), 
        suits = suits[0:int(ParamApp.getValue('limit'))],
        location = request.form.get('location',''),
        gender = request.form.get('gender',''),
        element = request.form.get('element',''),
        size = request.form.get('size',''),
        epoque = request.form.get('epoque',''),
        state = request.form.get('state',''),
        color = request.form.get('color',''),
        dispo = request.form.get('dispo',''),
        haut = request.form.get('haut',''),
        robe = request.form.get('robe',''),
        ensemble = request.form.get('ensemble',''),
        accessoire = request.form.get('accessoire',''),
        description = request.form.get('description',''), 
        titlehome=ParamApp.getValue('titlehome'), 
        bannerhome=ParamApp.getValue('bannerhome')
        )

def searchsuit(id):
    suit = Suit.get(id=id)
    if suit is not None:
        return render_template('suitview.html', suit=suit, listofvalue=getlistofvalue())
    return "<div></div>"

class Search(Blueprint):
    def __init__(self, name='search', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/search', 'search', search, methods=['GET'])
        self.add_url_rule('/search', 'searchsuits', searchsuits, methods=['POST'])
        self.add_url_rule('/search/<int:id>', 'searchsuit', searchsuit, methods=['GET'])

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
        except:
            app.logger.error("init search on register is failed")