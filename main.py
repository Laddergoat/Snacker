import os
import jinja2
import urllib
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    userEnd = ndb.UserProperty()

    @staticmethod
    def getcurrentuser():
        currentuser = users.get_current_user()
        if currentuser:
            lookup = User.query(User.email == currentuser.email())
            fetchresult = lookup.fetch()
            for fetchresult in fetchresult:
                return fetchresult.name

        else:
            return False


class Images(ndb.Model):
    file_name = ndb.StringProperty()
    url = ndb.StringProperty()
    uploader = ndb.StringProperty()


class Comment(ndb.Model):
    content = ndb.StringProperty()
    commentId = ndb.IntegerProperty()


class HomePage(webapp2.RequestHandler):
    def get(self):
        currentuser = users.get_current_user()
        currentusername = User().getcurrentuser()
        upload_url = blobstore.create_upload_url('/upload')
        if currentuser:
            greeting = "<a href='%s'>Log out</a>" % users.create_logout_url('/')
            qry = User.query(User.email == currentuser.email())
            getresult = qry.fetch()
            if getresult:
                userexistance = True
            else:
                u = User(email=currentuser.email(), name=currentuser.nickname(), userEnd=users.get_current_user())
                u.put()
        else:
            greeting = "<a href='%s'>Log In </a>" % users.create_login_url('/')

        qry = Images.query()
        images = qry.fetch()
        template_values = {
            "upload_url": upload_url,
            "currentUser": currentuser,
            "username": currentusername,
            "logout": greeting,
            "images": images
        }

        template = jinja_environment.get_template('templates/index.html')
        self.response.write(template.render(template_values))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/upload/%s' % blob_info.key())


class DetailsHandler(webapp2.RequestHandler):
    def get(self, resource):
        currentuser = users.get_current_user().email()
        image = Images(uploader=currentuser, url=resource, file_name="TEST")
        image.put()

        self.redirect('/')


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


class UserHandler(webapp2.RequestHandler):
    def get(self, resource):
        upload_url = blobstore.create_upload_url('/upload')
        currentuser = users.get_current_user()
        currentusername = User().getcurrentuser()
        resource = str(urllib.unquote(resource))
        qry = User.query(User.name == resource.lower())
        results = qry.fetch()

        if results:
            status = "User Found"
            self.response.write(status)

        else:
            status = "User Not Found"
            self.response.write(status)

        template_values = {
            "upload_url": upload_url,
            "user": results,
            "currentUser": currentuser,
            "username": currentusername,
            "loggedIn": currentuser
        }

        template = jinja_environment.get_template('templates/user.html')
        self.response.write(template.render(template_values))


class CaptureHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('templates/capture.html')

        self.response.write(template.render())

app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/upload', UploadHandler),
    ('/upload/([^/]+)?', DetailsHandler),
    ('/serve/([^/]+)?', ServeHandler),
    ('/capture', CaptureHandler),
    ('/([^/]+)?', UserHandler)],
    debug=True)
