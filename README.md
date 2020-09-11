# itly-sdk-python
Iteratively Analytics SDK for Python

## Run unit tests

### Install pytest

```
pip install pytest pytest-httpserver
```

### Run tests

```
pytest
```

## Build and publish packages

### Prerequisites

#### Install Poetry

[Installation](https://python-poetry.org/docs/#installation)

#### If Test PyPi used

1. Generate API token on ["Account Settings" page](https://test.pypi.org/manage/account/)

2. Add Test PyPi to Poetry config: `poetry config repositories.testpypi https://test.pypi.org/legacy/`

3. Add the Test PyPi token: `poetry config pypi-token.testpypi TOKEN` 

#### If real PyPi used

1. Generate API token on ["Account Settings" page](https://pypi.org/manage/account/)

2. Add the PyPi token: `poetry config pypi-token.pypi TOKEN` 


### Build packages

1. Increase versions in `pyproject.toml` files for affected packages.

2. Build affected packages. Example `make build-sdk build-segment`

### Publish packages to Test PyPi

`make publish-test-all`

### Publish packages to real PyPi

`make publish-all`
