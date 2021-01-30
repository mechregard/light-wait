import logging
import datetime
from pathlib import Path
from shutil import copyfile
from shutil import copy2
import pkg_resources
import configparser
from distutils.dir_util import copy_tree
from itertools import cycle
from jinja2 import Environment, FileSystemLoader
import markdown
import json
from feedgen.feed import FeedGenerator
from .exception import LightwaitException


class LightWait(object):
    """

    Light and fast blogging platform to generate
    blog posts from your markdown

    minimal clean css focusing on standards and limited download size

    """

    # relative to stage path
    CONTENT = "content"
    TAG = "tag-"

    # directory names for HOME
    LIGHTWAIT_HOME = ".lightwait"
    MARKDOWN = "markdown"
    METADATA = "metadata"
    TEMPLATE = "template"
    WWW = "www"
    # USER modifiable config file
    CONFIG_FILE = 'lightwait.ini'

    def __init__(self):
        """
        Set up logging and prepare lightwait HOME directory contents
        This includes static files copied from the package, as well
        as directories to hold imported markdown and metadata

        If configuration/content exists under the lightwait HOME directory, then
        the content is NOT overwritten. This is so a user can modify
        this configuration or content.

        """
        logging.basicConfig(level=logging.INFO)
        home_path = Path('~').expanduser()
        self.base = home_path / self.LIGHTWAIT_HOME
        self.base.mkdir(exist_ok=True)
        self.markdown = self.base / self.MARKDOWN
        self.metadata = self.base / self.METADATA
        self.template = self.base / self.TEMPLATE
        self.www = self.base / self.WWW
        self.config_path =  self.base / self.CONFIG_FILE
        # if not installed in HOME then copy from package source
        if not self.template.exists():
            self._init_home([self.markdown, self.metadata, self.template, self.www])
            copyfile(pkg_resources.resource_filename(__package__, self.CONFIG_FILE), self.config_path.as_posix())
            copy_tree(pkg_resources.resource_filename(__package__, self.TEMPLATE), self.template.as_posix())
            copy_tree(pkg_resources.resource_filename(__package__, self.WWW), self.www.as_posix())
            logging.debug("Copied resources to: "+self.base.as_posix())
        else:
            logging.debug("Using existing: "+self.base.as_posix())
        # read modifiable config
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path.as_posix())
        self.URL = self.config.get('lw', 'url')

    def import_md(self, src, name, description, tags):
        """

        Given the source name of a markdown file, along with information about
        the file contents, copy the file to the lightwait HOME directory under
        a unique name and create metadata for the file.

        If the name given is not unique, toss an exception

        NOTE: an alternative import method could determine title, description
        and tags directly from the source markdown file, so bulk import of
        markdown could be supported

        """
        created = self._save_markdown(src, name)
        self._save_metadata(
            {
                "title": name,
                "description": description,
                "tags": tags,
                "date": created.strftime("%d %b %Y"),
            }
        )

    def generate(self, stage_dir):
        """

        Given the directory target for the generated content,
        generate blog posts from each metadata post
        and associated imported markdown file,
        generate main and tags indexes using metadata posts,
        generate rss feed using metadata posts

        """
        stage_path = self._prepare_stage(stage_dir)
        self._generate_posts(stage_path)
        self._generate_indexes(stage_path)
        self._generate_rss(stage_path)

    #
    # import functions, mainly metadata management

    def _init_home(self, subdirs):
        for d in subdirs:
            d.mkdir(exist_ok=True)

    def _save_markdown(self, src, name):
        markdown_name = name+'.md'
        markdown_path = self.markdown / markdown_name
        if not markdown_path.exists():
            copy2(src, markdown_path.as_posix())
            return datetime.datetime.fromtimestamp(markdown_path.stat().st_mtime)
        else:
            raise LightwaitException("Name for markdown already exists")

    def _save_metadata(self, metadata):
        self._update_posts_metadata(metadata)
        for tag in metadata["tags"]:
            self._update_tags(tag, metadata)
        logging.debug("Imported " + metadata["title"])

    def _update_posts_metadata(self, metadata):
        posts = self._get_posts_metadata()
        posts["posts"].append(metadata)
        posts_path = self.metadata / "posts.json"
        with posts_path.open("w") as outfile:
            json.dump(posts, outfile)

    def _update_tags(self, tag, metadata):
        tags = self._get_tags_metadata(tag)
        tags["posts"].append(metadata)
        tag_json = tag+".json"
        tags_path = self.metadata / tag_json
        with tags_path.open("w") as outfile:
            json.dump(tags, outfile)

    def _get_posts_metadata(self):
        posts_path = self.metadata / "posts.json"
        if posts_path.exists():
            with posts_path.open() as json_file:
                return json.load(json_file)
        else:
            return {"posts": []}

    def _get_tags_metadata(self, tag):
        tag_json = tag+".json"
        tags_path = self.metadata / tag_json
        if tags_path.exists():
            with tags_path.open() as json_file:
                return json.load(json_file)
        else:
            return {"tag": tag, "posts": []}

    def _get_all_tags(self, pj):
        tags = set()
        for p in pj["posts"]:
            for tag in p["tags"]:
                tags.add(tag)
        return tags

    #
    # Generate html

    def _prepare_stage(self, stage_dir):
        copy_tree(self.www.as_posix(), stage_dir)
        return Path(stage_dir)

    def _generate_posts(self, stage_path):
        pj = self._get_posts_metadata()
        for p in pj["posts"]:
            name = p["title"]
            post_dir = stage_path / self.CONTENT / name
            post_dir.mkdir(parents=True, exist_ok=True)
            post_file = post_dir / "index.html"
            # augment post with content from markdown
            p['content'] = self._get_content(name)
            self._render("post.index", post_file, p)
            logging.debug("generated " + name)

    def _generate_indexes(self, stage_path):
        pj = self._get_posts_metadata()
        tags = self._get_all_tags(pj)
        pj['tags'] = tags
        pj['blogtitle'] = self.config.get('lw', 'blogTitle')
        pj['blogsubtitle'] = self.config.get('lw', 'blogSubTitle')
        pj['tagline'] = self.config.get('lw', 'blogTagLine')

        main_path = stage_path / "index.html"
        self._render("main.index", main_path, pj)
        logging.debug("generated index.html")
        for tag in tags:
            filename = self.TAG + tag + ".html"
            tj = self._get_tags_metadata(tag)
            tag_path = stage_path / filename
            self._render("tag.index", tag_path, tj)
            logging.debug("generated tags " + tag)

    def _generate_rss(self, stage_path):
        feed = self._create_feed()
        pj = self._get_posts_metadata()
        for p in pj["posts"]:
            fe = feed.add_entry()
            fe.id(self.URL + "content/" + p["title"])
            fe.title(p["title"])
            fe.description(p["description"])
            terms = [{k: v} for k, v in zip(cycle(["term"]), p["tags"])]
            fe.category(terms)
            fe.link(href=self.URL + "content/" + p["title"], rel="alternate")
            fe.published(p["date"] + " 00:00:00 GMT")
        rss_path = stage_path / self.CONTENT / "rss.xml"
        feed.rss_file(rss_path.as_posix(), pretty=True)
        logging.debug("generated rss")

    def _create_feed(self):
        fg = FeedGenerator()
        fg.id(self.URL + "content")
        fg.title(self.config.get('lw', 'blogTitle'))
        fg.author({"name": self.config.get('lw', 'blogAuthor'), "email": self.config.get('lw', 'blogAuthorEmail')})
        fg.link(href=self.URL, rel="alternate")
        fg.logo(self.URL + "image/favicon.ico")
        fg.subtitle(self.config.get('lw', 'blogSubTitle'))
        fg.link(href=self.URL + "content/rss.xml", rel="self")
        fg.language(self.config.get('lw', 'blogLang'))
        return fg

    def _get_content(self, name):
        markdown_name = name + '.md'
        markdown_path = self.markdown / markdown_name
        text = markdown_path.read_text()
        return markdown.markdown(text)

    def _render(self, template_name, outfile, data):
        data['url'] = self.URL
        data['lang'] = self.config.get('lw', 'blogLang')
        data['copyright'] = self.config.get('lw', 'copyright')

        template = self._get_template(template_name)
        output = template.render(j=data)
        outfile.write_text(output)

    def _get_template(self, template_name):
        file_loader = FileSystemLoader(self.template)
        env = Environment(loader=file_loader)
        return env.get_template(template_name)
