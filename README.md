# ontology_manager
An RDFLib based Ontology Manager for Python. 


# Installation

## create a python virtual env

```
python -m venv /path/to/new/virtual/environment
```

example 
```
python3 -m venv ./.ontoenv

```
Now activate it: 

```
source ./.ontoenv/bin/activate

```

you need the GraphViz package installed, for both the visualisation in onto_manager and in protege. Visit https://graphviz.org/ and install for your system


Now install Onto_Manager: 
```
python insall . -e 
```

this will install base packages, but we need (recommended) to install jupyter notebook and start it

```
pip install jupyter 
jupyter notebook


```

