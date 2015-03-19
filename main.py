import os
import jinja2
import urllib
import webapp2

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class SnackerImage(ndb.Model):
    imageUrl = ndb.StringProperty()
    uploader = ndb.StringProperty()
    content = ndb.StringProperty()


class Comment(ndb.Model):
    content = ndb.StringProperty()
    commentId = ndb.IntegerProperty()


class HomePage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            self.redirect(users.create_login_url('/'))

        template = jinja_environment.get_template('templates/index.html')
        self.response.write(template.render())


class BlankPage(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        qry = Comment.query(Comment.commentId == 1)
        comments = qry.fetch()
        # Variables that should be accessible to the template
        template_values = {
            "comments": comments,
            "upload_url": upload_url
        }
        template = jinja_environment.get_template('templates/blank.html')
        # Post Template and assign values that are required
        self.response.write(template.render(template_values))

    def post(self):
        self.comment = Comment(content=self.request.get('post'), commentId=1)
        self.comment.put()


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/blank', BlankPage),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler)],
    debug=True)