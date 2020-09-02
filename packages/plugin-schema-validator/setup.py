from setuptools import setup, find_packages

setup(
    name='itly.plugin-schema-validator',
    version='0.0.9',
    description='Iteratively Analytics SDK - Schema Validator Plugin',
    long_description='Iteratively Analytics SDK - Schema Validator Plugin',
    url='https://github.com/iterativelyhq/itly-sdk-python',
    author='Iteratively',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
    install_requires=[
        'jsonschema',
        'itly.sdk',
    ],
)
