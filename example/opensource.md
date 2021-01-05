## Steps taken to open source Light-wait 

#### Create project and License in github
Review the different license models available on the github project create page. 
If there is one you would like that does not exist, you can always copy over a LICENSE text 
file to the project root later.

#### Create cookiecutter project
cookiecutter is a python tool to create default python projects. Install with pip
 
    pip install cookiecutter
    cookiecutter https://github.com/kragniz/cookiecutter-pypackage-minimal

#### Set up python environment for development
I am using pyenv/pipenv for virtual python runtimes and sandboxed dependencies. Lots of blog 
posts provide install details, but here is what I used from within
my new cookiecutter generated python project directory:
  
    pyenv install  3.8.2
    pyenv local 3.8.2
    pip install pipenv
    pipenv install
    pipenv shell


#### Setup tools 
Install twine and create a setup.py script to handle dependencies, packaging etc. 
A MANIFEST.in file can be used to selectively add/remove non-python files into the package.
An example of a non-python file in Light-wait is the css file.
Run the setup.py script with arguments for sdist and bdist:

    pipenv install twine
    python setup.py sdist bdist_wheel

#### Configure tests
Instal a test framework like pytest. The cookiecutter project will automatically create 
a dummy test directory and example test.


#### Create README
Light-wait follows a growing README movement which focuses on basic usage and how to 
get more information/contribute. Badges are included to highlight 
project characteristics. The Shields IO service provides ways to generate markdown 
links to dynamic badges, such as code size.

    https://shields.io/ 


#### Code Formatter
Install and run a code formatter. I used Black:

    pip install black
    black -t py37  -l 105 lightwait/lightwait.py 

#### Test packaging and deployment
A key step in open sourcing is making the package available for others to direcctly use. The python 
package repository pypi has a mirror https://test.pypi.org for testing your packaging and deploy. 
Create an account in both, and test out with test.pypi. Use twine to verify and upload your 
distribution to the test.pypi first:

    twine check dist/*
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

#### Veriy pip install from test.pypi
After you uploaded your distribution, go to the test.pypi.org site and verify your upload. The 
projects page will list your uploaded projects, and the project details page
will include a pip install command using this test repo:
 
    pip install -i https://test.pypi.org/simple/ lightwait 

#### create github release
See the fine docs here:

    https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/managing-releases-in-a-repository

#### Do packaging and deployment for real
Create https://pypi.org/ account and repeat what was done for the test:

    twine check dist/*
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*


#### Verify it all works!

     pip install lightwait

  

  
 
  

