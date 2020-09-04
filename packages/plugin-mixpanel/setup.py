from setuptools import setup

setup(
    name='itly.plugin-mixpanel',
    version='0.0.5',
    description='Iteratively Analytics SDK - Mixpanel Plugin',
    long_description='Iteratively Analytics SDK - Mixpanel Plugin',
    url='https://github.com/iterativelyhq/itly-sdk-python',
    author='Iteratively',
    license='MIT',
    packages=['itly.plugin_mixpanel'],
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
    install_requires=[
        'mixpanel',
        'itly.sdk',
    ],
)
