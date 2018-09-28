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

from time import sleep

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    trim_blocks=True)


@ndb.transactional
def insert_if_absent(tag_key, tag):
    fetch = tag_key.get()
    if fetch is None:
        tag.put()
        return True
    return False


class Tag(ndb.Model):
    type = ndb.StringProperty()

    @classmethod
    def query_by_type(cls, type):
        return cls.query(cls.type == type)


class Book(ndb.Model):
    name = ndb.StringProperty()
    tag = ndb.KeyProperty(kind=Tag, repeated=True)

    @classmethod
    def query_by_name(cls, name):
        return cls.query(cls.name == name)


class Greeting(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)


class BookPage(webapp2.RequestHandler):
    def get(self, book_id):
        book_key = ndb.Key("Book", int(book_id))
        book = book_key.get()
        greetings = Greeting.query_book(book_key).fetch(20)

        tags = []
        for tag_key in book.tag:
            tags.append(tag_key.id())

        template_values = {
            'book': book,
            'tags': tags,
            'greetings': greetings
        }
        template = JINJA_ENVIRONMENT.get_template('book.html')
        self.response.write(template.render(template_values))


class SubmitForm(webapp2.RequestHandler):
    def post(self, book_id):
        book_key = ndb.Key("Book", int(book_id))
        greeting = Greeting(parent=book_key,
                            content=self.request.get('content'))
        greeting.put()
        self.redirect('/books/' + book_id)


class UpdateForm(webapp2.RequestHandler):
    def post(self, book_id):
        new_guestbook_name = self.request.get('new_guestbook_name')
        book_key = ndb.Key("Book", int(book_id))
        book = book_key.get()
        book.name = new_guestbook_name
        book.put()
        sleep(0.1)
        self.redirect('/books/' + book_id)


class AddBook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        book = Book(name=guestbook_name)

        tag_type = self.request.get('tag_type')
        if tag_type:
            tag_key = ndb.Key('Tag', tag_type)
            tag = Tag(id=tag_type, type=tag_type)
            insert_if_absent(tag_key, tag)
            book.tag = [tag_key]

        book.put()
        sleep(0.1)
        self.redirect('/')


class BookList(webapp2.RequestHandler):
    def get(self):
        tag_type = self.request.get('tag')
        if tag_type:
            q = Tag.query_by_type(tag_type)
            tag_key = q.fetch(keys_only=True)[0]
            books_query = Book.query(Book.tag==tag_key).order(Book.name)
        else:
            books_query = Book.query().order(Book.name)
        books = books_query.fetch()
        template_values = {
            'books': books
        }
        template = JINJA_ENVIRONMENT.get_template('booklist.html')
        self.response.write(template.render(template_values))


class AddTag(webapp2.RequestHandler):
    def post(self, book_id):
        book_key = ndb.Key("Book", int(book_id))
        book = book_key.get()

        tag_keys = []
        for tag_key in book.tag:
            tag_keys.append(tag_key)

        tag_type = self.request.get('tag_type')
        tag_key = ndb.Key('Tag', tag_type)
        tag = Tag(id=tag_type, type=tag_type)

        if insert_if_absent(tag_key, tag):
            tag_keys.append(tag_key)

        book.tag = tag_keys
        book.put()
        self.redirect('/books/' + book_id)


class DeleteGreeting(webapp2.RequestHandler):
    def post(self, book_id, greeting_id):
        greeting_key = ndb.Key("Book", int(book_id), 'Greeting', int(greeting_id))
        greeting_key.delete()
        self.redirect('/books/' + book_id)


app = webapp2.WSGIApplication([
    webapp2.Route('/', handler=BookList, name='BookList'),
    webapp2.Route('/add_book', handler=AddBook),
    webapp2.Route('/books/<book_id>', handler=BookPage),
    webapp2.Route('/books/<book_id>/post', handler=SubmitForm),
    webapp2.Route('/books/<book_id>/update', handler=UpdateForm),
    webapp2.Route('/books/<book_id>/addtag', handler=AddTag),
    webapp2.Route('/books/<book_id>/<greeting_id>/delete', handler=DeleteGreeting)
])
# [END all]