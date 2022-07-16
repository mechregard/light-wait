## Steps taken to open source Light-wait 

#### Create project and License in github
Review the different license models available on the github project create page. 
If there is one you would like that does not exist, you can always copy over a LICENSE text 
file to the project root later.

#### Set up python environment for development
I am using pyenv/pipenv for virtual python runtimes and sandboxed dependencies. Lots of blog 
posts provide install details, but here is what I used from within
my new cookiecutter generated python project directory:
  
    pyenv install  3.8.2
    pyenv local 3.8.2
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

#### Create cookiecutter project
cookiecutter is a python tool to create default python projects. Install with pip
 
    pip install cookiecutter
    cookiecutter https://github.com/kragniz/cookiecutter-pypackage-minimal

#### Poetry dependencies  
Create poetry dependency management and build configuration file `pyproject.toml`

    poetry init

Update the `pyproject.toml` by adding dependencies for your project and for your development tooling. Use poetry
update to resolve dependency versions and set within the `poetry.lock` file. Run poetry install to install
the dependencies defined in the lock file. The poetry shell command provides a shell into the poetry virtual
environment for your project.

    poetry update
    poetry install
    poetry shell

#### Configure tests
Instal a test framework like pytest under the toml file dev tools dependency section. 
The cookiecutter project / poetry will automatically create a dummy test directory and example test.

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
Create an account in both, and test with test.pypi. 

First, build the project distribution. Make sure to first set the version in your toml file:

    poetry build

Point poetry to the testpypi repository using the poetry config command. Publish to the testpypi
repository with the publish command, providing the repository name:

    poetry config repositories.testpypi https://test.pypi.org/legacy/
    poetry publish -r testpypi

#### Veriy pip install from test.pypi
After you uploaded your distribution, go to the test.pypi.org site and verify your upload. The 
projects page will list your uploaded projects, and the project details page
will include a pip install command using this test repo:
 
    pip install -i https://test.pypi.org/simple/ lightwait 

#### create github release
To clarify the release process, I first created a release branch then created a github release
from that release branch. Details nicely stated here:

    https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/managing-releases-in-a-repository

#### Do packaging and deployment for real
Create https://pypi.org/ account and run publish with no arguments to publish to the real pypi index:

     poetry publish

#### Verify it all works!

     pip install lightwait

  

  
 
  

