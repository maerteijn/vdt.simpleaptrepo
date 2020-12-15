from setuptools import setup, find_packages

__version__ = "1.0.0"


setup(
    # package name in pypi
    name='vdt.simpleaptrepo',
    # extract version from module.
    version=__version__,
    description="A simple command line utility to create a debian repository",
    long_description=open('README.rst').read(),
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='',
    author='Martijn Jacobs',
    author_email='maerteijn@gmail.com',
    url='https://github.com/devopsconsulting/vdt.simpleaptrepo',
    license='BSD',
    # include all packages in the egg, except the test package.
    packages=find_packages(
        exclude=['ez_setup', 'examples', '*tests']),
    # for avoiding conflict have one namespace for all apc related eggs.
    namespace_packages=['vdt'],
    # include non python files
    include_package_data=True,
    zip_safe=False,
    # specify dependencies
    install_requires=[
        'setuptools',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'simpleapt = vdt.simpleaptrepo.cli:main',
        ]
    },
    # mark test target to require extras.
    extras_require={
        'dev': ['nose', 'coverage', 'mock', 'twine'],
    },
)
