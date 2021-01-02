import argparse
import os
import logging
from pathlib import Path
from distutils.dir_util import copy_tree
import datetime
from itertools import cycle
from jinja2 import Environment, FileSystemLoader
import markdown
import json
from feedgen.feed import FeedGenerator

class LightWait(object):
  """

    Light and fast blogging platform to generate
    blog posts from your markdown

    minimal clean css focusing on limited size and standards

  """
  URL='http://127.0.0.1/'

  # relative to stage path
  CONTENT='content'
  TAG='tag-'

  # relative to code
  WWW="www"
  MARKDOWN="markdown/"
  METADATA="metadata/"
  METADATA_POSTS=METADATA+"posts.json"

  def __init__(self):
    logging.basicConfig(level=logging.DEBUG)

  def post(self, name, description, tags):
    self._save_metadata({'title': name, 'description': description, 'tags': tags, 'date': datetime.datetime.now().strftime("%d %b %Y") })

  def generate(self, stage_dir):
    stage_path = self._prepare_stage(stage_dir)
    self._generate_posts(stage_path)
    self._generate_indexes(stage_path)
    self._generate_rss(stage_path)

#
# Metadata management
#   post.json
#   tagname.json
#

  def _save_metadata(self, metadata):
    self._update_posts_metadata(metadata)
    for tag in metadata['tags']:
      self._update_tags(tag, metadata)


  def _update_posts_metadata(self, metadata):
    pj = self._get_posts_metadata()
    pj["posts"].append(metadata)
    with open(self.METADATA_POSTS, 'w') as outfile:
      json.dump(pj, outfile)


  def _update_tags(self, tag, metadata):
    tj = self._get_tags_metadata(tag)
    tj["posts"].append(metadata)
    with open(self.METADATA+tag+'.json', 'w') as outfile:
      json.dump(tj, outfile)


  def _get_posts_metadata(self):
    posts_file = Path(self.METADATA_POSTS)
    if posts_file.exists():
      with open(self.METADATA_POSTS) as json_file:
        return json.load(json_file)
    else:
      return {'posts':[]} 

  def _get_tags_metadata(self, tag):
    tags_file = Path(self.METADATA+tag+'.json')
    if tags_file.exists():
      with tags_file.open() as json_file:
        return json.load(json_file)
    else:
      return {'tag': tag, 'posts':[]} 

  def _get_all_tags(self, pj):
    tags = set() 
    for p in pj['posts']:
      for tag in p['tags']:
        tags.add(tag) 
    return tags

#
# Generate html
#
#

  def _prepare_stage(self, stage_dir):
    copy_tree(self.WWW, stage_dir)
    return Path(stage_dir)

  def _generate_posts(self, stage_path):
    pj = self._get_posts_metadata()
    for p in pj['posts']:
      title = p['title']
      post_dir = stage_path / self.CONTENT / title
      post_dir.mkdir(parents=True, exist_ok=True)
      post_file = post_dir / 'index.html'
      # augment post with content from markdown
      p['content'] = self._get_content(title)
      self._render('post.index', post_file, p)
      logging.debug('generated '+title)

  def _generate_indexes(self, stage_path):
    pj = self._get_posts_metadata()
    tags = self._get_all_tags(pj)
    pj['tags'] = tags
    main_path = stage_path / 'index.html'
    self._render('main.index', main_path, pj)
    logging.debug('generated index.html')
    for tag in tags:
      filename=self.TAG+tag+".html"
      tj = self._get_tags_metadata(tag)
      tag_path = stage_path / filename 
      self._render('tag.index', tag_path, tj)
      logging.debug('generated tags '+tag)


  def _generate_rss(self, stage_path):
    feed = self._create_feed()
    pj = self._get_posts_metadata()
    for p in pj['posts']:
      fe = feed.add_entry()
      fe.id(self.URL+'content/'+p['title'])
      fe.title(p['title'])
      fe.description(p['description'])
      terms = [{k: v} for k, v in zip(cycle(['term']),p['tags'])]
      fe.category(terms)
      fe.link( href=self.URL+'content/'+p['title'], rel='alternate' )
      fe.published(p['date']+' 00:00:00 GMT')
    rss_path = stage_path / self.CONTENT / "rss.xml"
    feed.rss_file(str(rss_path), pretty=True)
    logging.debug('generated rss')

  def _create_feed(self):
    fg = FeedGenerator()
    fg.id(self.URL+'content')
    fg.title('Dive')
    fg.author( {'name':'dlange','email':'dlange@mechregard.dev'} )
    fg.link( href=self.URL, rel='alternate' )
    fg.logo(self.URL+'image/favicon.ico')
    fg.subtitle('development artificial intelligence')
    fg.link( href=self.URL+'content/rss.xml', rel='self' )
    fg.language('en')
    return fg

  def _get_content(self, name):
    src_path=Path(self.MARKDOWN+name+'.md')
    text = src_path.read_text()
    return markdown.markdown(text)

  def _render(self, template_name, outfile, data):
    template = self._get_template(template_name)
    output = template.render(j=data)
    outfile.write_text(output)
    
  def _get_template(self, template_name):
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    return env.get_template(template_name)

   
if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Generate blog post')
  parser.add_argument("-g", "--generate", help="generate")
  parser.add_argument("-n", "--name", type=str, help="name")
  parser.add_argument("-d", "--description", type=str, help="description")
  parser.add_argument("-t", "--tags", type=str, help="tags list")
  args = parser.parse_args()

  lw = LightWait()
  if args.generate:
    lw.generate(args.generate)
  else:
    lw.post(args.name, args.description, args.tags.split(','))

