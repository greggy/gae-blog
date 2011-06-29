# -*- coding: utf-8 -*-
import logging
import sys
sys.path[0:0] = ['distlib']

import os
from google.appengine.api import users
from google.appengine.ext import webapp
#from google.appengine.ext.webapp.template import render
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images

from wtforms import validators
from wtforms.ext.appengine.db import model_form

from models import *
from utils import render


# Forms
post = Post()
error_message = u'Это поле обязательно для заполнения.'
PostForm = model_form(Post, only=('title', 'slug', 'content', 'published'), field_args={
    'title': {
        'validators': [validators.Required(message = error_message)],
        'label': u'Заголовок'
    }, 'slug': {
        'validators': [validators.Required(message = error_message)],
        'label': u'Слаг'
    }, 'content': {
        'validators': [validators.Required(message = error_message)],
        'label': u'Тело статьи'
    }, 'published': {
        'label': u'Опубликовать'
    }
})
    
# Handlers
class MainHandler(webapp.RequestHandler):
    def get(self):
        posts = Post.all()
        posts.filter('published =', True).order('-date_posted').fetch(10)
        context = {
            #'user': user,
            'posts': posts[:10],
            'login': users.create_login_url(self.request.uri),
            'logout': users.create_logout_url(self.request.uri),
        }
        render(self, 'index.html', context)
        
class PostHandler(webapp.RequestHandler):
    def get(self, *args, **kwargs):
        post = db.Query(Post).filter('slug =', args[2]).get()
        context = {
            'post': post
        }
        admin = users.is_current_user_admin()
        if admin:
            context['is_admin'] = admin
        render(self, 'post_item.html', context)
        
    def delete(self):
        post = db.get(self.request.get('post_id'))
        if post:
            post.delete()
            context = {} 
            render(self, 'post_del.html', context)
        else:
            self.error(404)
            
class EditPostHandler(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        post = Post.get(db.Key.from_path('Post', id))
        data = {}
        form = PostForm(data=data, obj=post)
        context = {
            'form': form
        }
        render(self, 'post_add.html', context)
    
    def post(self):
        self.redirect("/")
        
class PostsHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        form = PostForm()
        context = {
            'form': form
        }
        render(self, 'post_add.html', context)
        
    def post(self):
        form = PostForm(self.request.POST)
        #print self.request.POST['tags'].split(','), dir(form)
        if form.validate():
            post.title = self.request.get('title')
            post.slug = self.request.get('slug')
            post.content = self.request.get('content')
            post.published = bool(self.request.get('published', False))
            post.put()
            # Insert tags to tag and recount it if tag exist in model 
            if self.request.POST['tags']:
                for tag_name in self.request.POST['tags'].split(','):
                    tag = Tag()
                    tag.post = post
                    tag.name = tag_name
                    tag.put()
                    try:
                        tag_exist = db.GqlQuery("SELECT * FROM Tags WHERE name = :1 ", tag_name)
                        tags = tag_exist.get()
                        #logging.info('Tag is in db.')
                        tags.count += 1
                    except:
                        tags = Tags()
                        tags.name = tag_name
                        tags.count = 1
                        logging.info('Tag is not in db.')
                    tags.put()
            image = self.request.get('image') 
            if image:
                photo = Photo()
                photo.post = post
                photo.image_full_size = db.Blob(image)
                image = images.resize(image, 250, 350)
                photo.image = db.Blob(image)
                photo.title = self.request.get('image_title') or image 
                photo.put()
            self.redirect("/")
        else:
            context = {
                'form': form
            }
            render(self, 'post_add.html', context)

class ImageHandler(webapp.RequestHandler):
    def get(self):
        photo = db.get(self.request.get("img_id"))
        if photo.image:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(photo.image)
        else:
            self.response.out.write("No image")

class TagHandler(webapp.RequestHandler):
    def get(self, *args):
        posts = db.Query(Tag).filter('name =', args[0]).get()
        context = {
            'posts': posts,
        }
        render(self, 'index.html', context)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/post', PostsHandler),
        ('/edit', EditPostHandler),
        ('/(\d\d\d\d)/(\d\d)/([-\w]+)', PostHandler),
        ('/img', ImageHandler),
        ('/tag/([-\w]+)', TagHandler),
    ], debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
