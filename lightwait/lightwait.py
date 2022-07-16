import logging
import hashlib
import json
from datetime import datetime
from distutils.dir_util import copy_tree
from itertools import takewhile, dropwhile, cycle
from pathlib import Path
from pathvalidate import sanitize_filename
from shutil import copyfile
from shutil import copy2
from typing import List, Set, Dict, Optional, Any
import pkg_resources
import configparser
from jinja2 import Environment, FileSystemLoader
import markdown
from feedgen.feed import FeedGenerator
from lightwait.exception import LightwaitException


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
    # all keys
    ALL_KEYS = [MD_TITLE, MD_DESCRIPTION, MD_TAGS, MD_DATE]

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
    # metadata file holding posts
    POSTS_METADATA_NAME = "lw_posts"
    RESERVED_NAMES = [POSTS_METADATA_NAME, ]
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
        home_path = self._get_home_path()
        self.base = home_path / LightWait.LIGHTWAIT_HOME
        self.markdown = self.base / LightWait.MARKDOWN
        self.metadata = self.base / LightWait.METADATA
        self.template = self.base / LightWait.TEMPLATE
        self.www = self.base / LightWait.WWW
        self.config_path = self.base / LightWait.CONFIG_FILE
        # if not installed in HOME then copy from package source
        if not self.base.exists():
            self._install_home_dir(self.base,
                                   self.markdown,
                                   self.metadata,
                                   self.template,
                                   self.www,
                                   self.config_path)
        else:
            logging.info(f"Using existing: {self.base.as_posix()}")
        # read modifiable config
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path.as_posix())
        self.URL = self.config.get('lw', 'url')
        self.docroot = Path(self.config.get('lw', 'docroot'))
        # functions which take single path param
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

    def generate(self, docroot: Optional[Path] = None) -> None:
        """
        Given the directory target for the generated content,
        generate blog posts from each metadata post
        and associated imported markdown file,
        generate main and tags indexes using metadata posts,
        generate rss feed using metadata posts

        @param docroot:
        @return:
        """
        logging.info(f"Args: {docroot=}")
        docroot = self.docroot if docroot is None else docroot
        stage_path = self._prepare_stage(docroot)
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
    # called by init to simplify testing
    def _get_home_path(self) -> Path:
        return Path('~').expanduser()

    def _install_home_dir(self,
                          base: Path,
                          markdown: Path,
                          metadata: Path,
                          template: Path,
                          www: Path,
                          config: Path):
        for d in [base, markdown, metadata, template, www]:
            d.mkdir(exist_ok=True)
        copyfile(pkg_resources.resource_filename(__package__, LightWait.CONFIG_FILE), config.as_posix())
        copy_tree(pkg_resources.resource_filename(__package__, LightWait.TEMPLATE), template.as_posix())
        copy_tree(pkg_resources.resource_filename(__package__, LightWait.WWW), www.as_posix())
        logging.info(f"Copied resources to: {base.as_posix()}")

    #
    # import functions, mainly metadata management

    def _input_metadata(self,
                        src_path: Path,
                        title: Optional[str],
                        desc: Optional[str],
                        tags: Optional[str]) -> Dict[str, Any]:
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
        if src in LightWait.RESERVED_NAMES:
            raise LightwaitException(f"Name {src} is reserved")
        return sanitize_filename(src.strip().replace(" ", "-"), replacement_text="-")

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
    def _gen_comment_metadata(key: str, value: str) -> str:
        return f"[//]: # ({key}:{value})\n"

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
                   metadata: Dict[str, Any]) -> None:
        markdown_name = metadata[LightWait.MD_TITLE] + '.md'
        markdown_path = self.markdown / markdown_name
        if not markdown_path.exists():
            copy2(src_path.as_posix(), markdown_path.as_posix())
            self._save_metadata(metadata)
        else:
            raise LightwaitException(f"Title {markdown_name} for markdown {src_path} already exists")

    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        self._update_metadata(LightWait.POSTS_METADATA_NAME, metadata)
        for tag in metadata[LightWait.MD_TAGS]:
            self._update_metadata(tag, metadata)

    def _update_metadata(self, name: str, metadata: Dict[str, Any]) -> None:
        posts = self._get_metadata(name)
        posts.append(metadata)
        self._put_metadata(name, posts)

    def _get_metadata(self, name: str) -> List[Dict[str, Any]]:
        sorted_posts = []
        filename = name + ".json"
        filepath = self.metadata / filename
        if filepath.exists():
            with filepath.open() as json_file:
                sorted_posts = self._sort_by_date(json.load(json_file))
        return sorted_posts

    def _put_metadata(self, name: str, posts: List[Dict[str, Any]]) -> None:
        filename = name + ".json"
        filepath = self.metadata / filename
        with filepath.open("w") as outfile:
            json.dump(posts, outfile)

    @staticmethod
    def _sort_by_date(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(posts, key=lambda x: datetime.strptime(x['date'], '%d %b %Y'), reverse=True)

    @staticmethod
    def _get_all_tags(posts: List[Dict[str, Any]]) -> Set:
        tags = set()
        for p in posts:
            for tag in p[LightWait.MD_TAGS]:
                tags.add(tag)
        return tags

    #
    # Generate html

    def _prepare_stage(self, stage_dir: Path) -> Path:
        copy_tree(self.www.as_posix(), stage_dir.as_posix())
        return stage_dir

    def _generate_posts(self, stage_path: Path) -> None:
        for post_render in self._get_metadata(LightWait.POSTS_METADATA_NAME):
            name = post_render["title"]
            post_dir = stage_path / self.CONTENT / name
            post_dir.mkdir(parents=True, exist_ok=True)
            post_file = post_dir / "index.html"
            # augment post with content from markdown
            post_render['content'] = self._get_content(name)
            self._render("post.index", post_file, post_render)
            logging.info(f"Generated {name}")

    def _generate_indexes(self, stage_path: Path) -> None:
        posts = self._get_metadata(LightWait.POSTS_METADATA_NAME)
        tags = self._get_all_tags(posts)

        index_render_data = {
            "tags": tags,
            "posts": posts,
            "blogtitle": self.config.get('lw', 'blogTitle'),
            "blogsubtitle": self.config.get('lw', 'blogSubTitle'),
            "tagline": self.config.get('lw', 'blogTagLine')
        }
        main_path = stage_path / "index.html"
        self._render("main.index", main_path, index_render_data)
        logging.info("Generated index.html")

        for tag in tags:
            filename = self.TAG + tag + ".html"
            tag_posts = self._get_metadata(tag)
            tag_render_data = {
                "tag": tag,
                "posts": tag_posts
            }
            tag_path = stage_path / filename
            self._render("tag.index", tag_path, tag_render_data)
            logging.info(f"Generated {tag} index")

    def _generate_rss(self, stage_path: Path) -> None:
        feed = self._create_feed()
        for post_metadata in reversed(self._get_metadata(LightWait.POSTS_METADATA_NAME)):
            fe = feed.add_entry()
            fe.id(self.URL + "content/" + post_metadata[LightWait.MD_TITLE])
            fe.title(post_metadata[LightWait.MD_TITLE])
            fe.description(post_metadata[LightWait.MD_DESCRIPTION])
            terms = [{k: v} for k, v in zip(cycle(["term"]), post_metadata[LightWait.MD_TAGS])]
            fe.category(terms)
            fe.link(href=self.URL + "content/" + post_metadata[LightWait.MD_TITLE], rel="alternate")
            fe.published(post_metadata[LightWait.MD_DATE] + " 00:00:00 GMT")
        rss_path = stage_path / self.CONTENT / "rss.xml"
        feed.rss_file(rss_path.as_posix(), pretty=True)
        logging.info("Generated RSS")

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

    def _generate_output(self, out_path: Path) -> None:
        for post_metadata in self._get_metadata(LightWait.POSTS_METADATA_NAME):
            markdown_doc = []
            for key in LightWait.ALL_KEYS:
                markdown_doc.append(
                    LightWait._gen_comment_metadata(key, post_metadata[key])
                )
            markdown_name = post_metadata[LightWait.MD_TITLE] + '.md'
            markdown_path = self.markdown / markdown_name
            out_full_path = out_path / markdown_name
            if markdown_path.exists():
                with open(markdown_path.as_posix(), 'r') as lines:
                    rs = list(dropwhile(lambda x: x.startswith(LightWait.MD_PREFIX), lines))
                markdown_doc.extend(rs)
                with open(out_full_path, 'w') as outfile:
                    outfile.write(''.join(markdown_doc))

    def _get_content(self, name: str) -> str:
        markdown_name = name + '.md'
        markdown_path = self.markdown / markdown_name
        text = markdown_path.read_text()
        return markdown.markdown(text)

    def _render(self, template_name: str, outfile: Path, data: Dict[str, Any]) -> None:
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
