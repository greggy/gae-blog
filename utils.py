# -*- coding: utf-8 -*-
import os
import logging

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, environment
from models import Tags

def tags_cloud():
    '''Get dict of tags, numbers.'''
    tags = Tags.all()
    tags_dict = []
    for tag in tags:
        tags_dict.append({'name': tag.name, 'size': tag.count * 10})
    return tags_dict


"""Custom filters for jinja2"""
def date(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)


def render(self, template_name, variables):
    template_dirs = []
    template_dirs.append(os.path.join(os.path.dirname(__file__), 'templates'))
    env = Environment(loader = FileSystemLoader(template_dirs))
    env.filters['date'] = date
    env.globals['tags'] = tags_cloud()
    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        raise TemplateNotFound(template_name)
    content = template.render(variables)
    self.response.out.write(content)
    
