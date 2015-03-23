import os
import jinja2
import urllib
import webapp2
from uuid import uuid4

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class User(ndb.Model):
    userid = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    index = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    joined = ndb.DateTimeProperty(auto_now_add=True, indexed=False)


    @staticmethod
    def getcurrentuser():
        currentuser = users.get_current_user()
        if currentuser:
            lookup = User.query(User.userid == currentuser.user_id())
            fetchresult = lookup.fetch()
            for fetchresult in fetchresult:
                return fetchresult.name

        else:
            return False


class Image(ndb.Model):
    blob_key = ndb.BlobKeyProperty()
    user = ndb.StringProperty(required=True)
    tags = ndb.StringProperty(repeated=True)
    description = ndb.StringProperty()
    uploaded = ndb.DateTimeProperty(auto_now_add=True)


class Follower(ndb.Model):
    user = ndb.StringProperty()
    follower = ndb.StringProperty()


class Likes(ndb.Model):
    image_key = ndb.StringProperty()
    user = ndb.StringProperty()


class HomePage(webapp2.RequestHandler):
    def get(self):
        currentuser = users.get_current_user()
        currentusername = User().getcurrentuser()
        upload_url = blobstore.create_upload_url('/upload')

        if currentuser:
            greeting = "<a href='%s'>Log out</a>" % users.create_logout_url('/')
            find = User.get_by_id(currentuser.user_id())
            if find:
                print("User Exists")
            else:
                guid = str(uuid4())
                user = User(userid=currentuser.user_id(), email=currentuser.email(), name=guid,
                            index=guid.lower())
                user.key = ndb.Key(User, currentuser.user_id())
                user.put()

        else:
            greeting = "<a href='%s'>Log In </a>" % users.create_login_url('/')

        qry = Image.query().order(-Image.uploaded)
        images = qry.fetch(10)

        template_values = {
            "upload_url": upload_url,
            "currentuser": currentuser,
            "username": currentusername,
            "log": greeting,
            "images": images
        }

        template = jinja_environment.get_template('templates/index.html')
        self.response.write(template.render(template_values))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        image = Image(user=users.get_current_user().user_id(), blob_key=upload.key())
        image.tags = []
        image.put()
        self.redirect('/')


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.response.headers["Content-Type"] = "image/png"
        self.response.headers.add_header("Max-Age", "604800")

        self.send_blob(blob_info, save_as=True)


class UserHandler(webapp2.RequestHandler):
    def get(self, resource):
        currentuser = users.get_current_user()
        currentusername = User().getcurrentuser()
        upload_url = blobstore.create_upload_url('/upload')
        resource = str(urllib.unquote(resource))
        qry = User.query(User.index == resource.lower())
        results = qry.fetch()

        template_values = {
            "upload_url": upload_url,
            "currentuser": currentuser,
            "username": currentusername,
            "user": results
        }

        if results:
            status = "User Found"
            self.response.write(status)

        else:
            status = "User Not Found"
            self.response.write(status)

        template = jinja_environment.get_template('templates/user.html')
        self.response.write(template.render(template_values))


class CaptureHandler(webapp2.RequestHandler):
    def get(self):
        currentuser = users.get_current_user()
        currentusername = User().getcurrentuser()
        upload_url = blobstore.create_upload_url('/upload')

        template_values = {
            "upload_url": upload_url,
            "currentuser": currentuser,
            "username": currentusername
        }

        if currentuser:
            template = jinja_environment.get_template('templates/capture.html')
            self.response.write(template.render(template_values))

        else:
            self.redirect(users.create_login_url('/'))

app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler),
    ('/capture', CaptureHandler),
    ('/([^/]+)?', UserHandler)],
    debug=True)
