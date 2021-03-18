# itly-sdk-python
Iteratively Analytics SDK for Python

## Prerequisites
1. Install Python (3+)
    ```
    $ brew install python
    ```
2. [Install poetry](https://python-poetry.org/docs/#installation)

## Setup
* Create & activate virtual environment
    ```
    $ python -m venv venv && source venv/bin/activate
    ```

* Install project development dependencies (e.g. pytest pytest-httpserver)
    ```
    $ pip install -r requirements.txt
    ```
* Install dependencies for subpackages
    ```
    $ make install-all
    ```

## Test
* Run [pytest](https://docs.pytest.org/en/stable/)
    ```
    $ pytest
    ```

## Build
1. Increase versions in `pyproject.toml` files for affected packages.
2. Build affected packages.
    ```
    # Build a single package 
    $ make build-sdk
    
    # Build multiple packages
    $ make build-iteratively build-segment ...
    
    # Build all packages
    $ make build-all
    ```

## Publishing

### Setup PyPi Account & Token
1. Create an account on [pypi.org](https://pypi.org/).
2. Generate API token in [Account Settings](https://pypi.org/manage/account/)
3. Add PyPi token to Poetry config
    ```
    poetry config pypi-token.pypi TOKEN
    ``` 
   
### Publish

* PyPi (Production)
    ```
    $ make publish-all
    ```

## Teardown (for a fresh start)
* Deactivate & delete virtual environment
    ```
    $ deactivate && rm -rf venv
    ```

## Installing local SDK/plugins

* !!! Virtual environment should be used.

    ```
    pip install requests mixpanel jsonschema analytics-python
    
    pip install YOUR-PATH/itly-sdk-python/packages/sdk
    pip install YOUR-PATH/itly-sdk-python/packages/plugin-amplitude
    pip install YOUR-PATH/itly-sdk-python/packages/plugin-iteratively
    pip install YOUR-PATH/itly-sdk-python/packages/plugin-mixpanel
    pip install YOUR-PATH/itly-sdk-python/packages/plugin-schema-validator
    pip install YOUR-PATH/itly-sdk-python/packages/plugin-segment
    pip install YOUR-PATH/itly-sdk-python/packages/plugin-snowplow
    ```
