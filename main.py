import jinja2
import os
import webapp2
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class HomePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            greeting = ("Hello %s! (<a href ='%s'>Sign Out!</a>)" % (user.nickname(), users.create_logout_url('/')))
            self.response.write(greeting)
        else:
            self.redirect(users.create_login_url(self.request.uri))

        template= jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render())



app = webapp2.WSGIApplication([
    ('/', HomePage)],
    debug=True)
