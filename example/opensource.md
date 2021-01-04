## steps in open source

1. Create project and License in github

2. Create cookiecutter project
  pip install cookiecutter
  pyenv install  3.8.2
  pyenv local 3.8.2
  pyenv versions
  pip install pipenv
  pipenv install -e .
  pipenv shell
  cookiecutter https://github.com/kragniz/cookiecutter-pypackage-minimal

3. Setuptools setup.py
  pipenv install twine
  vi MANIFEST.in 
  python setup.py sdist bdist_wheel

4. Configure tests

5. Creaete README

6. Install and run formatter (black)

7. Create https://test.pypi.org/ test account

8. Verify package and upload to test.pypi
  twine check dist/*
  twine upload --repository-url https://test.pypi.org/legacy/ dist/*

9. Veriy pip install from test.pypi

10. create github release

11. Create https://pypi.org/ account

12. Verify package and upload to pypi

https://medium.com/free-code-camp/from-a-python-project-to-an-open-source-package-an-a-to-z-guide-c34cb7139a22

https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/managing-releases-in-a-repository

Setting up lighttpd
  brew install lighttpd
  cat /usr/local/etc/lighttpd/lighttpd.conf 
  vi /usr/local/etc/lighttpd/lighttpd.conf 
  brew services start lighttpd
  vi /usr/local/etc/lighttpd/lighttpd.conf 
  cd /usr/local/var/www/htdocs
  

  
 
  

