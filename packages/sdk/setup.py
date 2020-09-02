from setuptools import setup, find_packages

setup(
    name='itly.sdk',
    version='0.0.18',
    description='Iteratively Analytics SDK',
    long_description='Iteratively Analytics SDK',
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
        "six",
        'future; python_version == "2.7"',
        'enum34; python_version == "2.7"',
        'typing; python_version == "2.7"'
    ],
)
