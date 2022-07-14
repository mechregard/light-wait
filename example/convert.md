poetry build

poetry config repositories.testpypi https://test.pypi.org/legacy/

poetry config pypi-token.testpypi <token>
or
poetry publish -r testpypi -u <username> -p <password> --dry-run
poetry publish -r testpypi -u <username> -p <password>

