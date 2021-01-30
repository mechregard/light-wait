from setuptools import setup
from os import path

DIR = path.dirname(path.abspath(__file__))

with open(path.join(DIR, 'README.md')) as f:
    README = f.read()


setup(
    name='lightwait',
    packages=['lightwait'],
    description="Light-wait produces the bare minimum blog content from markdown files",
    long_description=README,
    long_description_content_type='text/markdown',
    install_requires=[
        'jinja2',
        'markdown',
        'feedgen'
    ],
    version='0.0.2',
    url='http://github.com/mechregard/light-wait',
    author='dlange',
    author_email='dave.lange@gmail.com',
    keywords=['blog', 'cms'],
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest'
    ],
    include_package_data=True,
    
    entry_points={
        "console_scripts": [
            "lightwait=lightwait.__main__:main",
        ]
    },
    python_requires='>=3.7'
)
