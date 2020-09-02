from setuptools import setup, find_packages

setup(
    name='itly.plugin-iteratively',
    version='0.0.4',
    description='Iteratively Analytics SDK - Iteratively Plugin',
    long_description='Iteratively Analytics SDK - Iteratively Plugin',
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
        'requests',
        'six',
        'itly.sdk',
    ],
)
