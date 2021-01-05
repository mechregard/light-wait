
![light-wait](img/light-wait-logo.png)

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/mechregard/light-wait)
[![License: CC0-1.0](https://img.shields.io/badge/License-CC0%201.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
![Keybase PGP](https://img.shields.io/keybase/pgp/dlange)

`light-wait` is a blogging platform to produce light (as in features), minimal wait (as in fast to download) web content from markdown.

Light-wait produces the bare minimum blog content from markdown files:
* overview and per-tag (category) indexes
* RSS feed
* configuration file to simplify customization 

Here is an example screen-shot of blog content:

![GIF demo](img/screen.png)


## Usage

```
Usage: python light-wait.py [OPTIONS]

  Generate blog content from markdown


optional arguments:
  -c COMMAND, --command COMMAND # import or generate
  
  -f FILE, --file FILE          # import src markdown file path
  -n NAME, --name NAME          # import short unique name
  -d DESCRIPTION, --description DESCRIPTION  # import description
  -t TAGS, --tags TAGS          # import tag (category) list
  
  -o OUTPUT, --output OUTPUT    # generate output directory
                        
  -h, --help                    # show this help message and exit  
```

## Quick Start

1. Install with pip

    + `$ pip install lightwait`

Use light-wait to generate blog content from existing markdown. First, import your markdown files, 
providing a unique name, description and a list of tags. The name will be used in the URL of 
the blog post, so it needs to be URL friendly.
 
In this example, a markdown about signs is imported:

```
 $ lightwait -c import -f /some/markdown.md -n signs -d 'a new take on signs' -t traffic
```

To generate the static site content from the imported markdown, use the generate  command,
providing the output directory:

```
 $ lightwait -c generate -o /usr/local/var/www/
```

The generated content can be directly placed into a docroot of a locally running web server like above, 
or staged and transferred to a remote host. The URL is configurable (see Configuration Options below).
A python web server can be used to verify the content:

```
 $ cd /usr/local/var/www/
 $ python3 -m http.server
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

The most important user-defined configurations are held in the `lightwait.ini` file. This
is a python INI file (see configparser), containing a default configuration section and the 
possibility to have multiple overriding configuration sections.

Light-wait uses the `lw` section and inherits all the defaults. The simplist way to configure
is to update all of the default properties and not have any override properties.

An example of using an override property is to be able to test locally but deploy remotely:

```INI
[DEFAULT]
url = http://localhost:9009/

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
 $ ls
 lightwait.ini	markdown	metadata	template	www
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

Now generate content using light-wait:

```
 $ lightwait -c generate -o /usr/local/var/www/
```

Then open a browser to http://localhost:8080/

##Tool Chain and Frameworks
The following frameworks and tools enable Light-wait:

* https://python-markdown.github.io/
* https://jinja.palletsprojects.com/en/2.11.x/
* https://feedgen.kiesow.be/
* https://github.com/psf/black
* https://shields.io/
* https://twine.readthedocs.io/en/latest/
* https://pypi.org/

Details are provided under the `example` markdown


**How to Contribute**
---

1. Clone repo and create a new branch: `$ git checkout https://github.com/mechregard/light-wait -b name_for_new_branch`.
2. Make changes and test
3. Submit Pull Request with comprehensive description of changes


**Donations**
---

This is free, open-source software. 


Image credit goes to: https://dauntlessfightclub.net/
