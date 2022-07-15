import logging
from lightwait.lightwait import LightWait
from pathlib import Path
from distutils.dir_util import copy_tree
from shutil import copyfile
import pkg_resources
import configparser


class NoInitLightWait(LightWait):
    def __init__(self):
        home_path = Path(pkg_resources.resource_filename(__name__, "resources/home"))
        self.base = home_path / LightWait.LIGHTWAIT_HOME
        self.base.mkdir(exist_ok=True)
        self.markdown = self.base / LightWait.MARKDOWN
        self.metadata = self.base / LightWait.METADATA
        self.template = self.base / LightWait.TEMPLATE
        self.www = self.base / LightWait.WWW
        self.config_path = self.base / LightWait.CONFIG_FILE
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
        self.URL = "testurl"
        # functions which take single path param
        self.md_generator = {
            LightWait.MD_TITLE: LightWait._gen_title,
            LightWait.MD_DESCRIPTION: LightWait._gen_description,
            LightWait.MD_TAGS: LightWait._gen_tag,
            LightWait.MD_DATE: LightWait._gen_date
        }


class TestLightWait():

    def test_all_metadata(self):
        lw = NoInitLightWait()
        fn=pkg_resources.resource_filename(__name__, "resources/allmetadata.md")
        md = lw._input_metadata(Path(fn), None, None, None)
        assert md["tags"] == ['research']
        assert md["title"] is not None
        assert md["description"] is not None
        assert md["date"] is not None

    def test_no_metadata(self):
        lw = NoInitLightWait()
        fn=pkg_resources.resource_filename(__name__, "resources/nometadata.md")
        md = lw._input_metadata(Path(fn), None, None, None)
        assert md["tags"] == ['general']
        assert md["title"] == '14-Jul-2022_ad8a0b'
        assert md["description"] == 'Heading'
        assert md["date"] == '14 Jul 2022'

    def test_partial_metadata(self):
        lw = NoInitLightWait()
        fn=pkg_resources.resource_filename(__name__, "resources/partialmetadata.md")
        md = lw._input_metadata(Path(fn), None, None, None)
        assert md["tags"] == ['tag1', 'tag2']
        assert md["title"] == '14-Jul-2022_b5188e'
        assert md["description"] == 'Heading'
        assert md["date"] == '14 Jul 2022'

    def test_override_metadata(self):
        lw = NoInitLightWait()
        fn=pkg_resources.resource_filename(__name__, "resources/allmetadata.md")
        md = lw._input_metadata(Path(fn), "override-title", "override-desc", None)
        assert md["tags"] == ['research']
        assert md["title"] == "override-title"
        assert md["description"] == "override-desc"
        assert md["date"] is not None

    def test_tag_set(self):
        lw = NoInitLightWait()
        pj = [{"title": "title", "description": "desc", "tags": ["aaa","aaa"]}]
        assert lw._get_all_tags(pj) == {"aaa"}

    def test_to_posixt(self):
        lw = NoInitLightWait()
        assert lw._to_posix("with a blanks") == "with-a-blanks"
        assert lw._to_posix(" end-blanks ") == "end-blanks"
        assert lw._to_posix("a mix?of*things") == "a-mix-of-things"
