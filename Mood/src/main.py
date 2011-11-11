'''
Created on Oct 30, 2011

@author: daniel
'''
import os, random,logging

import json
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

latinAndGreek = ['vol', 'viv', 'vit', 'ven', 'van', 'vel','zo', 'urb', 'urg', 'unc', 'ulo', 'trin',
            'trem', 'tri', 'tot', 'tim', 'the', 'tep', 'tax', 'sud', 'sui', 'styl', 'sten', 'su',
            'st', 'son', 'sol', 'sil', 'ser', 'sen', 'sei','sed', 'seb', 'sfi', 'sax', 'san',
            'sax', 'rur', 'rug', 'rot', 'rog', 'rod', 'rhe', 'ren', 'rar', 'ran', 'rad', 'ras',
            'qui', 'put', 'pur', 'pup', 'pto', 'pro', 'pre', 'pot', 'pon', 'por', 'pol', 'pod',
            'plu', 'pis', 'pir', 'pin', 'pil', 'pic', 'pet', 'per', 'pen', 'ped','pav', 'pat',
            'pan', 'pam', 'pal', 'pac', 'oxy', 'ovi', 'ov', 'ot','orn','or', 'opt', 'oo', 'ont',
            'omo', 'omm', 'oma',  'ole', 'oen', 'oed', 'od', 'oct', 'ob', 'o', 'oc', 'os', 'nuc',
            'nub', 'nu', 'nox', 'noc', 'nov', 'not', 'non', 'nod', 'nes', 'neg', 'nav', 'nas', 'nar',
            'myz', 'myx', 'my', 'mut', 'mus', 'mur', 'mov', 'mot', 'mon', 'mol', 'mne', 'mit', 'mis',
            'mir', 'min', 'mim', 'mic', 'mes', 'mer', 'mei', 'mar', 'man', 'mal', 'maj', 'lun', 'lud',
            'lus', 'luc', 'log', 'loc', 'lin', 'lig', 'lev', 'lep', 'leg', 'lax', 'lav', 'lat', 'lab',
            'juv', 'jut', 'jus', 'jur', 'jug', 'joc', 'jac', 'is', 'iso', 'in', 'il', 'im', 'ir', 
            'ign', 'idi', 'ide', 'id', 'hor', 'hod', 'hex', 'hen', 'hai', 'hei', 'hab', 'hib', 'gyn',
            'ger', 'gen', 'gel', 'ge', 'geo', 'fur', 'fum', 'fug', 'for', 'flu', 'fl', 'fin', 'fil',
            'fic', 'fis', 'fet','fer', 'fel', 'fat', 'fab','exo', 'ex', 'ef', 'eur', 'eu', 'eso',
            'err', 'erg', 'equ', 'iqu', 'epi', 'ep', 'ens', 'en', 'em', 'eme', 'ego', 'eg', 'ed', 
            'es', 'ec', 'eco', 'dys', 'dy', 'dur', 'dub', 'du', 'dom', 'dia', 'di', 'den', 'deb', 
            'de', 'cyt', 'cut', 'cub', 'cre', 'con', 'co', 'col', 'com', 'cor', 'col', 'civ', 'cen',
            'ced', 'cav', 'can', 'cap', 'cip', 'can', 'cin', 'cad', 'cis', 'cas', 'cac', 'bov',
            'bor', 'bon', 'bi', 'bio', 'bib', 'bi', 'ben', 'be', 'bac', 'axi', 'avi', 'aut', 'aur',
            'aud', 'ar', 'aqu', 'apo', 'ant', 'ann', 'enn', 'ana', 'an', 'am', 'alb', 'ad', 'ac', 
            'af', 'ag', 'al', 'ap', 'ar', 'as', 'at', 'acr', 'ac', 'ab', 'abs']

def generateName(numberOfRoots, numberOfWords):
    """Generate a name from the number of roots"""
    listOfNames = []
    for _ in range(numberOfWords):
        name = ""
        for _ in range(numberOfRoots):
            name += latinAndGreek[random.randint(0, len(latinAndGreek) - 1)]
        listOfNames.append(str(name))
    return listOfNames


class User(db.Model):
    """The user of the application"""
    Id = db.StringProperty()
    age = db.IntegerProperty()
    sex = db.IntegerProperty()
    totalAnswers = db.IntegerProperty()

class Question(db.Model):
    """Get the equstion of a model"""
    answer_list = db.StringListProperty()
    question = db.StringProperty()
    
    def toJSON(self):
        """Return the JSON of the question"""
        return {"class" : "Question", "value": {'answer_list' : self.answer_list,
                                                'question' : self.question}}
class Answer(db.Model):
    """Get the answer of the model"""
    location = db.GeoPtProperty()
    degree = db.FloatProperty()
    answer = db.StringProperty()
    user = db.ReferenceProperty(User)
    answerNumber = db.FloatProperty()               # The number of answers
    question = db.ReferenceProperty(Question)
    
class RPCHandler(webapp.RequestHandler):
    """ Allows the functions defined in the RPCMethods class to be RPCed."""
    def __init__(self):
        webapp.RequestHandler.__init__(self)
        self.methods = RPCMethods()

    def get(self):
        func = None

        action = self.request.get('action')
        if action:
            if action[0] == '_':
                self.error(403) # access denied
                return
            else:
                func = getattr(self.methods, action, None)

        if not func:
            self.error(404) # file not found
            return

        args = ()
        while True:
            key = 'arg%d' % len(args)
            val = str(self.request.get(key))
            logging.error(val.__class__)
            logging.error(val)
            if val:
                args += (json.loads(val),)
            else:
                break
        result = func(*args)
        self.response.out.write(json.dumps(result))

    def post(self):
        args = json.loads(self.request.body)
        func, args = args[0], args[1:]

        if func[0] == '_':
            self.error(403) # access denied
            return

        func = getattr(self.methods, func, None)
        if not func:
            self.error(404) # file not found
            return

        result = func(*args)
        self.response.out.write(json.dumps(result))

class RPCMethods:
    """ 
    Defines the methods that can be RPCed.
    """

    def Add(self, *args):
        """Add any object into the database"""
        if args[0] == "Question":
            return self._AddQuestion(json.loads(args[1]))
        elif args[0] == "Answer":
            return self._AddAnswer(args[1])
        elif args[0] == "User":
            return self._AddUser(args[1])
        else:
            return False
        
    def Get(self, *args):
        """Get any object into the database"""
        if args[0] == "Question":
            return self._GetQuestion(args[1])
        elif args[0] == "UserAnswer":
            return self._GetUserAnswers(args[1])

    # The add interface
    def _AddQuestion(self, cmd):
        """Add a question to the file"""
        q = Question()
        q.answer_list = [str(l) for l in cmd['answer_list']]
        q.question = cmd['question']
        q.put()
        return {'key' : q.key().name()}
    
    def _AddAnswer(self, cmd):
        """Add a answer to the database"""
        a = Answer()
        user = User.get_by_key_name(cmd['user'])
        a.user = user
        a.question = Question.get_by_key_name(cmd['question'])
        a.answer = cmd['answer']
        a.answerNumber = user.totalAnswers
 
        # Conditional answers
        if cmd.has_key('location'):
            a.location = db.GeoPt(float(cmd['location'][0]), float(cmd['latitude'][1]))
        if cmd.has_key('degree'):
            a.degree = float(cmd['degree'])
        
        # Update the server
        a.put()
        user.totalAnswers = user.totalAnswers + 1
        user.put()
        return {'key' : a.key().name()}
    
    def _AddUser(self, cmd):
        """Add a user to the database"""
        u = User()
        if cmd.has_key('age'):
            u.age = int(cmd['age'])
        if cmd.has_key('sex'):
            u.sex = int(cmd['sex'])
        u.Id = cmd['id']
        u.put()
        return {'key' : u.key().name()}
    
    # The get interface
    def _GetQuestion(self, cmd):
        """Get a question from the database"""
        
        logging.error(str(cmd))
        #raise ValueError("No JSON object could be decoded")json = simplejson.loads(cmd)
    
        if cmd.has_key('random'):
            q = Question()
            answer_list = []
           
            answer_list.extend(([" ".join( generateName(3, random.randint(1, 5)))  for _ in range(5) ]))
            q.answer_list = answer_list
            question = generateName(2, random.randint(0, 7))
            q.question = " ".join(question) + "?"
            return q.toJSON()
        return False
    
    def _GetUserAnswers(self, cmd):
        """Get the users answers"""
        user = User.get_by_key_name(cmd['user'])
        rangeList = [i for i in range(cmd['minrange'], cmd['maxrange'])]
        a = Answer.all().filter('user =', user).filter('answerNumber IN', rangeList)
        answerList = a.fetch(1000)
        return {'answerlist':answerList}
        
def main():
    app = webapp.WSGIApplication([
        ('/rpc', RPCHandler),
        ], debug=True)
    util.run_wsgi_app(app)

if __name__ == '__main__':
    main()