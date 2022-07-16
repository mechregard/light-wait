import os
from pathlib import Path
import click
from lightwait.lightwait import LightWait
from lightwait.exception import LightwaitException


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.obj = LightWait(debug)


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option('--title', '-n', default=None, help='Title of the post')
@click.option('--description', '-d', default=None, help='Description of the post')
@click.option('--tags', '-t', default=None, help='Tag or tag list')
@click.pass_obj
def post(lightwait: LightWait, file: Path, title: str, description: str, tags: str):
    """
    Create a blog post using FILE
    The initial lines in the FILE can describe metadata
    or optional parameters can define metadata
    """
    try:
        lightwait.post(file,
                       title=title,
                       description=description,
                       tags=tags)
        lightwait.generate()
        print(f"Published post for {file}")
    except LightwaitException as le:
        print(le)


@cli.command()
@click.argument('src_dir', type=click.Path(exists=True, path_type=Path))
@click.pass_obj
def post_all(lightwait: LightWait, src_dir: Path):
    """
    Create a blog post for each file in SRC_DIR
    The initial lines in each file can describe metadata
    """
    for file in os.listdir(src_dir.as_posix()):
        if file.endswith(".md"):
            file_path = os.path.join(src_dir.as_posix(), file)
            try:
                lightwait.post(Path(file_path))
                print(f"Created post for {file}")
            except LightwaitException as le:
                print(le)
    lightwait.generate()
    print(f"Published posts from {src_dir}")


@cli.command()
@click.option('--docroot', '-d',
              default=None,
              type=click.Path(exists=True, path_type=Path),
              help='Generate static content to this docroot')
@click.pass_obj
def generate(lightwait: LightWait, docroot: Path):
    """
    Create html and rss content within given DOCROOT
    """
    lightwait.generate(docroot)


@cli.command()
@click.argument('target_dir', type=click.Path(exists=True, path_type=Path))
@click.pass_obj
def export(lightwait: LightWait, target_dir: Path):
    """
    Export markdown of content to given TARGET_DIR
    """
    lightwait.export(target_dir)


if __name__ == "__main__":
    cli()
