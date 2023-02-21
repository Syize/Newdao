from setuptools import setup


setup(
    name='newdao',
    version='1.0',
    packages=['newdao'],
    package_data={'newdao': ['res/*', 'res/dict/*']},
    scripts=['scripts/nd.py']
)
