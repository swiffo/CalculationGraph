from os import path
import setuptools

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'Readme.Md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='calcgraph',
    version='0.1.1',
    description='A calculation graph with caching and overriding.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['calcgraph'],
)