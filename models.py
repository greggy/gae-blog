# -*- coding: utf-8 -*-
from google.appengine.ext import db


# Models
class Post(db.Model):
    title = db.StringProperty(multiline=False)
    slug = db.StringProperty(multiline=False)
    content = db.TextProperty()
    html_content = db.TextProperty()
    date_posted = db.DateTimeProperty(auto_now_add=True)
    published = db.BooleanProperty()
    
    def get_tags(self):
        return self.tag_set or None
    
    def tags_count(self):
        return self.tags_set.count() or None
    
    def get_photo(self):
        if self.photo_set.count() > 0:
            return self.photo_set[0]
        else:
            return None
    
class Photo(db.Model):
    post = db.ReferenceProperty(Post)
    title = db.StringProperty()
    image = db.BlobProperty()
    image_full_size = db.BlobProperty()

    
class Tag(db.Model):
    post = db.ReferenceProperty(Post)
    name = db.StringProperty()
    
class Tags(db.Model):
    '''Model to collect tags with count of using every tag.'''
    name = db.StringProperty()
    count = db.IntegerProperty()
