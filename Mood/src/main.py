'''
Created on Oct 30, 2011

@author: daniel
'''
import os

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

class User(db.Model):
    """The user of the application"""
    Id = db.StringProperty()
    age = db.IntegerProperty()
    sex = db.IntegerProperty()

class Question(db.Model):
    """Get the equstion of a model"""
    answer_list = db.StringListProperty()
    question = db.StringProperty()

class Answer(db.Model):
    """Get the answer of the model"""
    location = db.GeoPtProperty()
    user = db.ReferenceProperty(User)
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
            val = self.request.get(key)
            if val:
                args += (simplejson.loads(val),)
            else:
                break
        result = func(*args)
        self.response.out.write(simplejson.dumps(result))

    def post(self):
        args = simplejson.loads(self.request.body)
        func, args = args[0], args[1:]

        if func[0] == '_':
            self.error(403) # access denied
            return

        func = getattr(self.methods, func, None)
        if not func:
            self.error(404) # file not found
            return

        result = func(*args)
        self.response.out.write(simplejson.dumps(result))

class RPCMethods:
    """ 
    Defines the methods that can be RPCed.
    """

    def Add(self, *args):
        """Add any object into the database"""
        if args[0] == "Question":
            return self._AddQuestion(args[1])
        elif args[0] == "Answer":
            return self._AddAnswer(args[1])
        elif args[0] == "User":
            return self._AddUser(args[1])
        else:
            return False
        
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
        a.user = User.get_by_key_name(cmd['user'])
        a.question = Question.get_by_key_name(cmd['question'])
        a.location = db.GeoPt(cmd['location'][0], cmd['latitude'][1])
        a.put()
        return {'key' : a.key().name()}
    
    def _AddUser(self, cmd):
        """Add a user to the database"""
        u = User()
        if cmd.has_key('age'):
            u.age = cmd['age']
        if cmd.has_key('sex'):
            u.sex = cmd['sex']
        u.Id = cmd['id']
        u.put()
        return {'key' : u.key().name()}

def main():
    app = webapp.WSGIApplication([
        ('/rpc', RPCHandler),
        ], debug=True)
    util.run_wsgi_app(app)

if __name__ == '__main__':
    main()