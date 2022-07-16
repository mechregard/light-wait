
![light-wait](img/light-wait-logo.png)

![GitHub release (latest by date)](https://img.shields.io/github/v/release/mechregard/light-wait)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/mechregard/light-wait)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
![Keybase PGP](https://img.shields.io/keybase/pgp/dlange)
![PyPI](https://img.shields.io/pypi/v/lightwait)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/lightwait)

`light-wait` is a blogging platform to produce light (as in features), minimal wait (as in fast to download) web content from markdown.

Light-wait produces the bare minimum blog content from markdown files:
* overview and tag (category) indexes
* RSS feed
* configuration file to simplify customization 

Here is an example screen-shot of blog content:

![GIF demo](img/screen.png)


## Usage

```
Usage: lightwait [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --help    Show this message and exit.

Commands:
  export    Export markdown of content to given TARGET_DIR
  generate  Create html and rss content within given DOCROOT
  post      Create a blog post using FILE The initial lines in the FILE...
  post-all  Create a blog post for each file in SRC_DIR The initial lines...
```

## Quick Start

1. Install with pip

    + `$ pip install lightwait`

Use light-wait to generate blog content from existing markdown. Create a blog post from a single markdown
file, providing optional name, description and tags, or point to a directory of markdown files and create
posts from each file.
 
In this example, a post is created from a markdown file about opensource, and it is tagged 'software':

```
 $ lightwait post example/opensource.md -n opensourced -d 'How Light-wait was open-sourced' -t software
```

In this example, a post is created for each markdown file in the given directory `mydir`.

```
 $ lightwait post-all mydir/
```

Light-wait creates the static site content at the configured `docroot`directory, which by default
is at `/usr/local/var/www/`. 
A python web server can be used to verify the content:

```
 $ cd /usr/local/var/www/
 $ python3 -m http.server
```

## Post metadata
Each post is assigned the following metadata, either derived from the markdown file or overridden by 
command line arguments:

* title: default to markdown file create date and a hash of the file name
* description: default to first non-comment line of the markdown file
* tags: default to `general`
* date: default to markdown file create date

Additionally, a markdown file may contain this metadata as a comment at the start of the file:
```
[//]: # (tags:['general'])
```

## Configuration Options

Light-wait is designed with customization in mind. When Light-wait is first run, a directory 
is created under the user home directory. This is called `.lightwait` and it will hold
configuration, CSS, templates and imported markdown and metadata:

```
 $ cd ~/.lightwait
 $ ls
 lightwait.ini	markdown	metadata	template	www
 $
```
These files will only be copied if this initial set does not exist- you can freely modify
them, or if you wish to start over, remove them for Light-wait to re-initialize.

The most important user-defined configurations are held in the `lightwait.ini` file. 

This file contains the following properties, used to customize your static site:
```
url = http://localhost:8080/
blogTitle = title
blogSubTitle = subtitle
blogTagLine = tagLine
blogAuthor = author
blogAuthorEmail = author@example.com
blogLang = en
copyright = &copy; name date
docroot = /usr/local/var/www/
```

`lightwait.ini` is a python INI file (see configparser), containing a default configuration section and the 
possibility to have multiple overriding configuration sections. Light-wait uses the `lw` section and inherits all 
defaults. You can configure the defaults for your site and override specific properties based on how
you wish to deploy your static content.

An example of using an override property is to be able to test locally but deploy remotely:

```INI
[DEFAULT]
url = http://localhost:8080/

[lw]
url = http://some.domain/
```

Refer to the `example` directory for a fully configured INI.

Feel free to further customize the static content output by changing the templates (jinja2  format) or
css. These can be found here:

```
 ~/.lightwait/template/base.index  # Common including footer
 ~/.lightwait/template/main.index  # for main index.html
 ~/.lightwait/template/tag.index   # for tag-SOMETAG.html 
 ~/.lightwait/template/post.index  # for each post
 ~/.lightwait/www/css/main.css
```

The static site content can be re-generated from the posts at any time using the `generate` command. 
This has an optional docroot argument, allowing you to override the configuration setting:

```
 $ lightwait generate
```

## Running local web server Example
The following is an example of running lighttpd, a fast and lightweight web server,
and generating web content from markdown files, using Light-wait.

To install lighttpd on MacOS using homebrew

```
 $ brew update 
 $ brew install lighttpd
 $ brew services start lighttpd
```

This installs a default configuration file `/usr/local/etc/lighttpd/lighttpd.conf`
 and a docroot at `/usr/local/var/www`

Then open a browser to http://localhost:8080/

## Exporting your markdown
You can export all of your markdown content to a directory using the `export` command. This additionally
will add post metadata, such as any description or tags, as markdown comments at the top of each file.
Here is an example of exporting all markdown data to the directory `exportdir`:
```
 $ lightwait export ./exportdir
```

## Tool Chain and Frameworks
The following frameworks and tools enable Light-wait:

* https://python-markdown.github.io/
* https://jinja.palletsprojects.com/en/2.11.x/
* https://feedgen.kiesow.be/
* https://palletsprojects.com/p/click/
* https://github.com/psf/black
* https://shields.io/
* https://pypi.org/

Details are provided under the `example` markdown

## How to Contribute
1. Clone repo and create a new branch: `$ git checkout https://github.com/mechregard/light-wait -b name_for_new_branch`.
2. Make changes and test with `pytest` and `tox` (for testing on different versions of python)
3. Submit Pull Request with comprehensive description of changes

## Donations
This is free, open-source software. 


Image credit goes to: https://dauntlessfightclub.net/
