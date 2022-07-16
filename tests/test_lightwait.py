from lightwait.lightwait import LightWait
from pathlib import Path
import pkg_resources


class NoInitLightWait(LightWait):

    def _get_home_path(self) -> Path:
        return Path(pkg_resources.resource_filename(__name__, "resources/home"))

    def _install_home_dir(self,
                          base: Path,
                          markdown: Path,
                          metadata: Path,
                          template: Path,
                          www: Path,
                          config: Path):
        pass


class TestLightWait():

    def test_all_metadata(self):
        lw = NoInitLightWait(True)
        fn=pkg_resources.resource_filename(__name__, "resources/allmetadata.md")
        md = lw._input_metadata(Path(fn), None, None, None)
        assert md["tags"] == ['research']
        assert md["title"] is not None
        assert md["description"] is not None
        assert md["date"] is not None

    def test_no_metadata(self):
        lw = NoInitLightWait(True)
        fn=pkg_resources.resource_filename(__name__, "resources/nometadata.md")
        md = lw._input_metadata(Path(fn), None, None, None)
        assert md["tags"] == ['general']
        assert md["title"] == '14-Jul-2022_ad8a0b'
        assert md["description"] == 'Heading'
        assert md["date"] == '14 Jul 2022'

    def test_partial_metadata(self):
        lw = NoInitLightWait(True)
        fn=pkg_resources.resource_filename(__name__, "resources/partialmetadata.md")
        md = lw._input_metadata(Path(fn), None, None, None)
        assert md["tags"] == ['tag1', 'tag2']
        assert md["title"] == '14-Jul-2022_b5188e'
        assert md["description"] == 'Heading'
        assert md["date"] == '14 Jul 2022'

    def test_override_metadata(self):
        lw = NoInitLightWait(True)
        fn=pkg_resources.resource_filename(__name__, "resources/allmetadata.md")
        md = lw._input_metadata(Path(fn), "override-title", "override-desc", None)
        assert md["tags"] == ['research']
        assert md["title"] == "override-title"
        assert md["description"] == "override-desc"
        assert md["date"] is not None

    def test_tag_set(self):
        lw = NoInitLightWait(True)
        pj = [{"title": "title", "description": "desc", "tags": ["aaa","aaa"]}]
        assert lw._get_all_tags(pj) == {"aaa"}

    def test_to_posixt(self):
        lw = NoInitLightWait(True)
        assert lw._to_posix("with a blanks") == "with-a-blanks"
        assert lw._to_posix(" end-blanks ") == "end-blanks"
        assert lw._to_posix("a mix?of*things") == "a-mix-of-things"

    def test_config(self):
        lw = NoInitLightWait(True)
        assert lw.config.get('lw', 'blogTitle') == "Test Title"
        assert lw.config.get('lw', 'blogSubTitle') == "Test Sub"
