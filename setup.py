from setuptools import setup, find_packages

setup(
    name='ontology_manager',
    version='0.01',
    packages=find_packages(),
    description='An utility package for managing ontologies using RDFLib',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='The DDMD Team (C) Adham Hashibon',
    author_email='',
    url='https://github.com/materials-discovery/ontology_manager.git',
    install_requires=[
        'rdflib',  # Add other dependencies as needed
    ],
)

