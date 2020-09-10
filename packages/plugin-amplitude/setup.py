from setuptools import setup

setup(
    name='itly.plugin-amplitude',
    version='0.0.8',
    description='Iteratively Analytics SDK - Amplitude Plugin',
    long_description='Iteratively Analytics SDK - Amplitude Plugin',
    url='https://github.com/iterativelyhq/itly-sdk-python',
    author='Iteratively',
    license='MIT',
    packages=['itly.plugin_amplitude'],
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
        'requests',
        'itly.sdk',
    ],
)
