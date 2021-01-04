from lightwait import LightWait


class NoInitLightWait(LightWait):
    def __init__(self):
        pass


def test_tag_set():
    lw = NoInitLightWait()
    pj = {"posts": [{"title": "title", "description": "desc", "tags": ["aaa","aaa"]}]}
    assert lw._get_all_tags(pj) == {"aaa"}
