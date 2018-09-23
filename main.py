# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Cloud Datastore NDB API guestbook sample.

This sample is used on this page:
    https://cloud.google.com/appengine/docs/python/ndb/

For more information, see README.md
"""

# [START all]
import os
import cgi
import textwrap
import urllib

from google.appengine.ext import ndb

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Book(ndb.Model):
    name = ndb.StringProperty()

# [START greeting]
class Greeting(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]

# [START query]
    @classmethod
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)


class BookPage(webapp2.RequestHandler):
    def get(self, guestbook_name):
        ancestor_key = ndb.Key("Book", guestbook_name or "*notitle*")
        greetings = Greeting.query_book(ancestor_key).fetch(20)
# [END query]
        template_values = {
            'guestbook_name': guestbook_name,
            'greetings': greetings
        }
        template = JINJA_ENVIRONMENT.get_template('book.html')
        self.response.write(template.render(template_values))


# [START submit]
class SubmitForm(webapp2.RequestHandler):
    def post(self, guestbook_name):
        greeting = Greeting(parent=ndb.Key("Book",
                                           guestbook_name or "*notitle*"),
                            content=self.request.get('content'))
        greeting.put()
# [END submit]
        self.redirect('/books/' + guestbook_name)


class AddBook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        book = Book(id=guestbook_name,
                    name=guestbook_name)
        book.put()
        self.redirect('/')


class BookList(webapp2.RequestHandler):
    def get(self):
        books_query = Book.query().order(Book.name)
        books = books_query.fetch()
        template_values = {
            'books': books
        }
        template = JINJA_ENVIRONMENT.get_template('booklist.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    webapp2.Route('/', handler=BookList, name='BookList'),
    webapp2.Route('/add_book', handler=AddBook),
    webapp2.Route('/books/<guestbook_name>', handler=BookPage),
    webapp2.Route('/books/<guestbook_name>/post', handler=SubmitForm)
])
# [END all]