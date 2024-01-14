from setuptools import setup, find_packages

setup(
    name='ontodot',
    version='1.0',
    description='RDF Graph dot Visualizer',
    packages=find_packages(),
    install_requires=[
        'rdflib',
        'pydotplus',
        'ipython',
    ],
)

