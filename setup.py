from distutils.core import setup

setup(
    name='hey_april',
    version='1.0.5',
    author='Paul Heymann',
    author_email='hey_april@heymann.be',
    url='http://www.pybrid.com/',
    packages=['hey_april', ],
    package_data={'hey_april':
                  ['templates/*.html',
                   'assets/*/*/*.css',
                   'assets/*/*/*.js',
                   'assets/*/*/*.png',
                   'assets/*/*.js',
                 ]},
    license='LICENSE.txt',
    description='Hey! April Templating System',
    long_description=open('README.rst').read(),
    install_requires=[
        'jinja2',
    ]
)
