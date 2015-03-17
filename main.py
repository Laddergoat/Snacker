import jinja2
import os
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Comment(ndb.Model):
    content = ndb.StringProperty()
    commentId = ndb.IntegerProperty()

class HomePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user == False:
            self.redirect(users.create_login_url(self.request.uri))
            #greeting = ("Hello %s! (<a href ='%s'>Sign Out!</a>)" % (user.nickname(), users.create_logout_url('/')))
            #self.response.write(greeting)
        #else:


        template= jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render())

class BlankPage(webapp2.RequestHandler):
    def get(self):
        qry = Comment.query(Comment.commentId == 1)
        comments = qry.fetch()
        template_values = {
            "comments" : comments
        }
        template = jinja_environment.get_template('templates/blank.html')
        self.response.write(template.render(template_values))

        """for self.comment in qry.fetch(10):
            self.response.write('<p>%s</p>' % self.comment.content)"""

    def post(self):
        self.comment = Comment(content=self.request.get('post'), commentId=1)
        self.comment.put()
        self.redirect('/blank')

class SubForm(webapp2.RequestHandler):
    def get(self):
        self.redirect('/blank')

app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/blank', BlankPage),
    ('/sub', SubForm)],
    debug=True)
