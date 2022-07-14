import logging
from datetime import datetime
from typing import List, Set, Dict, Optional
from pathlib import Path
from pathvalidate import sanitize_filename
from itertools import takewhile
from shutil import copyfile
from shutil import copy2
import hashlib
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
    # metadata keys
    MD_TITLE = "title"
    MD_DESCRIPTION = "description"
    MD_TAGS = "tags"
    MD_DATE = "date"

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
    # Markdown comment prefix
    MD_PREFIX = "[//]: #"

    def __init__(self, debug: bool):
        """
        Set up logging and prepare lightwait HOME directory contents
        This includes static files copied from the package, as well
        as directories to hold imported markdown and metadata

        If configuration/content exists under the lightwait HOME directory, then
        the content is NOT overwritten. This is so a user can modify
        this configuration or content.

        """
        logging.basicConfig(format="%(levelname)s:%(funcName)s:%(message)s",
                            level=logging.DEBUG if debug else logging.ERROR)
        home_path = Path('~').expanduser()
        self.base = home_path / self.LIGHTWAIT_HOME
        self.base.mkdir(exist_ok=True)
        self.markdown = self.base / self.MARKDOWN
        self.metadata = self.base / self.METADATA
        self.template = self.base / self.TEMPLATE
        self.www = self.base / self.WWW
        self.config_path = self.base / self.CONFIG_FILE
        # if not installed in HOME then copy from package source
        if not self.template.exists():
            self._init_home([self.markdown, self.metadata, self.template, self.www])
            copyfile(pkg_resources.resource_filename(__package__, self.CONFIG_FILE), self.config_path.as_posix())
            copy_tree(pkg_resources.resource_filename(__package__, self.TEMPLATE), self.template.as_posix())
            copy_tree(pkg_resources.resource_filename(__package__, self.WWW), self.www.as_posix())
            logging.info(f"Copied resources to: {self.base.as_posix()}")
        else:
            logging.info(f"Using existing: {self.base.as_posix()}")
        # read modifiable config
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path.as_posix())
        self.URL = self.config.get('lw', 'url')
        # functions
        self.md_generator = {
            LightWait.MD_TITLE: LightWait._gen_title,
            LightWait.MD_DESCRIPTION: LightWait._gen_description,
            LightWait.MD_TAGS: LightWait._gen_tag,
            LightWait.MD_DATE: LightWait._gen_date
        }

    def post(self,
             src_path: Path,
             title: Optional[str] = None,
             description: Optional[str] = None,
             tags: Optional[str] = None) -> None:
        """
        Given the source name of a markdown file, along with information about
        the file contents, create a 'post':
          - copy the file to the lightwait HOME directory under a unique name
          - update 'posts' file with post metadata
          - update 'tags' file with post per tag metadata

        @param src_path:
        @param title:
        @param description:
        @param tags:
        @return:
        """
        logging.info(f"Args: {src_path=} {title=} {description=} {tags=}")
        metadata = self._input_metadata(src_path, title, description, tags)
        logging.info(f"Generated metadata: {metadata}")
        self._save_data(src_path, metadata)

    def generate(self, target_dir: Path) -> None:
        """
        Given the directory target for the generated content,
        generate blog posts from each metadata post
        and associated imported markdown file,
        generate main and tags indexes using metadata posts,
        generate rss feed using metadata posts

        @param target_dir:
        @return:
        """
        logging.info(f"Args: {target_dir=}")
        stage_path = self._prepare_stage(target_dir)
        self._generate_posts(stage_path)
        self._generate_indexes(stage_path)
        self._generate_rss(stage_path)

    def export(self, target_dir: Path) -> None:
        """
        @param target_dir:
        @return:
        """
        logging.info(f"Args: {target_dir=}")
        self._generate_output(target_dir)

    #
    # import functions, mainly metadata management

    def _input_metadata(self,
                        src_path: Path,
                        title: Optional[str],
                        desc: Optional[str],
                        tags: Optional[str]) -> Dict[str, str]:
        """
        Given a path to some markdown and a set of optional arguments,
        answer back a fixed set of metadata.
        """
        file_md = self._parse_file_metadata(src_path)

        # override any file metadata with any provided arguments
        title = file_md.get(LightWait.MD_TITLE) if title is None else title
        desc = file_md.get(LightWait.MD_DESCRIPTION) if desc is None else desc
        tags = file_md.get(LightWait.MD_TAGS) if tags is None else tags
        return {
            LightWait.MD_TITLE: LightWait._to_posix(title),
            LightWait.MD_DESCRIPTION: desc,
            LightWait.MD_TAGS: [LightWait._to_posix(tag) for tag in tags.split(",")],
            LightWait.MD_DATE: file_md.get(LightWait.MD_DATE)
        }

    @staticmethod
    def _to_posix(src: str) -> str:
        return sanitize_filename(src.replace(" ", "-"), replacement_text="-")

    @staticmethod
    def _init_home(subdirs: List[Path]) -> None:
        for d in subdirs:
            d.mkdir(exist_ok=True)

    def _parse_file_metadata(self, src_path: Path) -> Dict[str, str]:
        with open(src_path) as lines:
            rs = list(takewhile(lambda x: x.startswith(LightWait.MD_PREFIX), lines))
        metadata = LightWait._parse_comment_metadata(rs)
        for k in self.md_generator.keys():
            if k not in metadata:
                metadata[k] = self.md_generator[k](src_path)
        return metadata

    @staticmethod
    def _parse_comment_metadata(lines: List[str]) -> Dict[str, str]:
        """format of line is
            [//]: # (key:value)
        """
        matched = {}
        for li in lines:
            match = li[li.find("(") + 1:li.find(")")].split(":")
            matched[match[0]] = match[1]
        return matched

    @staticmethod
    def _gen_title(src_path: Path) -> str:
        date = LightWait._gen_date(src_path)
        uniq = hashlib.sha256(src_path.as_posix().encode('utf-8')).hexdigest()[:6]
        title = f"{date}_{uniq}"
        return title

    @staticmethod
    def _gen_description(src_path: Path) -> str:
        with open(src_path) as lines:
            for line in lines.readlines():
                if not line.startswith(LightWait.MD_PREFIX):
                    candidate = line.strip(' #\n')
                    if len(candidate) > 0:
                        return candidate
        return "no good description"

    @staticmethod
    def _gen_tag(file_path: Path) -> str:
        return "general"

    @staticmethod
    def _gen_date(file_path: Path) -> str:
        stamp = datetime.fromtimestamp(file_path.stat().st_mtime)
        return stamp.strftime("%d %b %Y")

    def _save_data(self,
                   src_path: Path,
                   metadata: Dict[str, str]) -> None:
        markdown_name = metadata[LightWait.MD_TITLE] + '.md'
        markdown_path = self.markdown / markdown_name
        if not markdown_path.exists():
            copy2(src_path.as_posix(), markdown_path.as_posix())
            self._save_metadata(metadata)
        else:
            raise LightwaitException(f"Title {markdown_name} for markdown {src_path} already exists")

    def _save_metadata(self, metadata: Dict) -> None:
        self._update_posts_metadata(metadata)
        for tag in metadata["tags"]:
            self._update_tags(tag, metadata)

    def _update_posts_metadata(self, metadata: Dict) -> None:
        posts = self._get_posts_metadata()
        posts["posts"].append(metadata)
        self._put_posts_metadata(posts)

    def _update_tags(self, tag: str, metadata: Dict[str,str]) -> None:
        tags = self._get_tags_metadata(tag)
        tags["posts"].append(metadata)
        self._put_tags_metadata(tag, tags)

    def _get_posts_metadata(self) -> Dict:
        sorted_posts = []
        posts_path = self.metadata / "posts.json"
        if posts_path.exists():
            with posts_path.open() as json_file:
                sorted_posts = self._sort_by_date(json.load(json_file)["posts"])
        return {
            "posts": sorted_posts
        }

    def _put_posts_metadata(self, posts: Dict) -> None:
        posts_path = self.metadata / "posts.json"
        with posts_path.open("w") as outfile:
            json.dump(posts, outfile)

    def _get_tags_metadata(self, tag: str) -> Dict:
        sorted_posts = []
        tag_json = tag + ".json"
        tags_path = self.metadata / tag_json
        if tags_path.exists():
            with tags_path.open() as json_file:
                sorted_posts = self._sort_by_date(json.load(json_file)["posts"])
        return {
            "tag": tag,
            "posts": sorted_posts
        }

    def _put_tags_metadata(self, tag: str, tags: Dict) -> None:
        tag_json = tag + ".json"
        tags_path = self.metadata / tag_json
        with tags_path.open("w") as outfile:
            json.dump(tags, outfile)

    @staticmethod
    def _sort_by_date(posts: List) -> List:
        return sorted(posts, key=lambda x: datetime.strptime(x['date'], '%d %b %Y'), reverse=True)

    @staticmethod
    def _get_all_tags(pj: Dict) -> Set:
        tags = set()
        for p in pj["posts"]:
            for tag in p["tags"]:
                tags.add(tag)
        return tags

    #
    # Generate html

    def _prepare_stage(self, stage_dir: Path) -> Path:
        copy_tree(self.www.as_posix(), stage_dir.as_posix())
        return stage_dir

    def _generate_posts(self, stage_path: Path) -> None:
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

    def _generate_indexes(self, stage_path: Path) -> None:
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

    def _generate_rss(self, stage_path: Path) -> None:
        feed = self._create_feed()
        pj = self._get_posts_metadata()
        for p in reversed(pj["posts"]):
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

    def _generate_output(self, out_path: Path) -> None:
        pj = self._get_posts_metadata()
        for p in pj["posts"]:
            tags = ",".join(p['tags'])
            markdown_name = p['title'] + '.md'
            markdown_path = self.markdown / markdown_name
            out_full_path = out_path / markdown_name
            if markdown_path.exists():
                with open(markdown_path.as_posix(), 'r') as f:
                    content = f.read()
                markdown = "description:" + p['description'] + '\n'
                markdown += "tags:" + tags + '\n'
                markdown += "date:" + p['date'] + '\n'
                markdown += content
                with open(out_full_path, 'w') as ff:
                    ff.write(markdown)

    def _create_feed(self) -> FeedGenerator:
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

    def _get_content(self, name: str) -> str:
        markdown_name = name + '.md'
        markdown_path = self.markdown / markdown_name
        text = markdown_path.read_text()
        return markdown.markdown(text)

    def _render(self, template_name: str, outfile: Path, data: Dict) -> None:
        data['url'] = self.URL
        data['lang'] = self.config.get('lw', 'blogLang')
        data['copyright'] = self.config.get('lw', 'copyright')

        template = self._get_template(template_name)
        output = template.render(j=data)
        outfile.write_text(output)

    def _get_template(self, template_name: str):
        file_loader = FileSystemLoader(self.template)
        env = Environment(loader=file_loader)
        return env.get_template(template_name)
