import os
import jinja2
import urllib
import webapp2
import cgi


from PIL import Image
from uuid import uuid4
from google.appengine.api import images
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


class Photo(ndb.Model):
    blob_key = ndb.BlobKeyProperty()
    user = ndb.StringProperty(required=True)
    tags = ndb.StringProperty(repeated=True)
    description = ndb.StringProperty()
    uploaded = ndb.DateTimeProperty(auto_now_add=True)


class Follower(ndb.Model):
    user = ndb.StringProperty()
    follower = ndb.StringProperty()


class Likes(ndb.Model):
    photo_key = ndb.StringProperty()
    user = ndb.StringProperty()


class HomePage(webapp2.RequestHandler):
    def get(self):
        currentuser = users.get_current_user()
        username = User().getcurrentuser()
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

        qry = Photo.query().order(-Photo.uploaded)
        photo = qry.fetch(10)

        template_values = {
            "upload_url": upload_url,
            "check": currentuser,
            "username": username,
            "log": greeting,

            "image": photo
        }

        template = jinja_environment.get_template('templates/home.html')
        self.response.write(template.render(template_values))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        photo = Photo(user=users.get_current_user().user_id(), blob_key=upload.key())
        photo.tags = []
        photo.put()
        self.redirect('/')


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        img = images.Image(blob_key=resource)
        img.resize(width=500, height=500)
        img.im_feeling_lucky()
        thumbnail = img.execute_transforms(output_encoding=images.JPEG)

        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(thumbnail)
        return


class ThumbHandler(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        img = images.Image(blob_key=resource)
        img.resize(width=200, height=200)
        img.im_feeling_lucky()
        thumbnail = img.execute_transforms(output_encoding=images.JPEG)

        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(thumbnail)
        return

class UserHandler(webapp2.RequestHandler):
    def get(self, resource):
        currentuser = users.get_current_user()

        username = User().getcurrentuser()
        upload_url = blobstore.create_upload_url('/upload')
        resource = str(urllib.unquote(resource))
        qry = User.query(User.index == resource.lower())
        results = qry.fetch()
        userid = None
        for user in results:
            userid = user.userid

        imgqry = Photo.query(userid == Photo.user)
        photo = imgqry.fetch()

        if currentuser:
            greeting = "<a href='%s'>Log out</a>" % users.create_logout_url('/')
            checkid = currentuser.user_id()

        else:
            greeting = "<a href='%s'>Log In </a>" % users.create_login_url('/')
            checkid = None

        template_values = {
            "upload_url": upload_url,
            "check": currentuser,
            "username": username,
            "log": greeting,

            "checkid": checkid,
            "userid": userid,
            "user": results,
            "image": photo
        }

        template = jinja_environment.get_template('templates/user.html')
        self.response.write(template.render(template_values))

    def post(self, resource):
        currentuser = users.get_current_user().user_id()
        name = cgi.escape(self.request.get('name'))
        current = User.get_by_id(currentuser)
        current.name = name
        current.index = name.lower()
        current.put()
        self.redirect('/%s' % name)





class CaptureHandler(webapp2.RequestHandler):
    def get(self):
        currentuser = users.get_current_user()
        username = User().getcurrentuser()
        upload_url = blobstore.create_upload_url('/upload')

        if currentuser:
            greeting = "<a href='%s'>Log out</a>" % users.create_logout_url('/')

        else:
            greeting = "<a href='%s'>Log In </a>" % users.create_login_url('/')

        template_values = {
            "upload_url": upload_url,
            "check": currentuser,
            "username": username,
            "log": greeting,
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
    ('/thumb/([^/]+)?', ThumbHandler),
    ('/capture', CaptureHandler),
    ('/([^/]+)?', UserHandler),
    ], debug=True)
