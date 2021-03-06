.. InPhO documentation master file, created by
   sphinx-quickstart on Tue Nov  8 15:10:48 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to InPhO's documentation!
=================================
The `Indiana Philosophy Ontology (InPhO) Project
<https://inpho.cogs.indiana.edu>`_ is a pragmatic attempt to model the
discipline of philosophy using an iterative three-step process known as 
**dynamic ontology**:

1.  **Data mining** - Natural Language Processing (NLP) techniques are used to
    generate statistical hypotheses about the relations among various topics in
    the SEP.
2.  **Expert feedback** - These hypotheses are evaluated by domain experts through
    online interfaces.
3.  **Machine reasoning** - The feedback is combined with the statistical measures
    as a knowledge base for our machine reasoning program, which uses answer set
    programming to output a taxonomic view of the discipline.

Before starting this process, a *term list* and *seed taxonomy* must first be created.
The *term list* can be auto-generated by using the `inphosemantics package
<http://github.com/inpho/inphosemantics>`_. It can be extracted from a current
inpho database by using the command ``python inpho/model/idea.py --export [-f
filename]``.

Modules
=========

.. toctree::
   :maxdepth: 2
   
   corpus 
   dlv
   lib
   model
   taxonomy
   module

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

