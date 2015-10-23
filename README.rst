.. image:: https://codeclimate.com/github/lliendo/Radar/badges/gpa.svg
   :target: https://codeclimate.com/github/lliendo/Radar
   :alt: Code Climate


.. image:: https://api.travis-ci.org/lliendo/Radar.svg?branch=master
    :target: https://travis-ci.org/lliendo/Radar
    :alt: Travis CI


Radar
=====

Radar is a general purpose monitoring system. It aims to be simple and extendable.
It uses arbitrary check execution and server side plugins to provide flexibility.
It is entirely written in the `Python <https://www.python.org/>`_ programming language and is distributed
under the GNU LGPLv3 license.


Installation
------------

Currently the only way to install Radar is through its source code (PyPI packages
are not yet available, mainly because the project is in ALPHA status).

Clone this repository to a temporary directory using `GIT <https://git-scm.com/>`_ (or alternatively download
as `.zip <https://github.com/lliendo/Radar/archive/master.zip>`_), and run  :

.. code-block:: bash

    git clone https://github.com/lliendo/Radar.git
    cd Radar
    python setup.py install


Documentation
-------------

You can read how to setup and use Radar (both client and server) from `here <http://radar-monitoring.readthedocs.org/en/latest/>`_.
You can also generate the documentation of the project by yourself using `Sphinx <http://sphinx-doc.org/>`_.

Radar does not include Sphinx in its dependencies so to generate the documentation
you will first need to install it :

.. code-block:: bash

    cd Radar
    pip install -r docs-requirements.txt

Now from the project's main directory run :

.. code-block:: bash

    cd Radar/docs
    build-doc.py

Sphinx will output the generated documentation to the 'docs/_build/html' directory.
To read the generated docs open up a browser and then load the index.html file.
The documentation is available in the following languages :

* English.
* Spanish.

To generate non-english versions (currently only spanish is available) of the
documentation you need to run :

.. code-block:: bash

    cd Radar/docs
    build-doc.py -l es

Once again, Sphinx will output the generated documentation to the 'docs/_build'
directory.

If you think that documentation is incomplete or not clear enough, please let
me know !


Status
------

Radar is currently in ALPHA status, however its foundations are complete.
You can take a look at the `limitations <http://radar-monitoring.readthedocs.org/en/latest/limitations.html>`_ section of the documentation to have
an idea what features are going to (or might) be implemented in the future.


Supported platforms
-------------------

Radar should run without any problems as long as the Python interpreter on your
platform is able to run.


Development
-----------

If you're interested in how Radar works you are encouraged to take a look at
the code, documentation about its internal ideas can be found `here <http://radar-monitoring.readthedocs.org/en/latest/internals.html>`_.
Radar is aimed to be both simple and easy to use and understand.


Tests
-----

Radar-Checks uses `Nose <https://nose.readthedocs.org/en/latest/>`_ to run its tests.
To install Nose, from the command line run :

.. code-block:: bash
    
    pip install nose

To run the tests, clone the this repository and run Nose.

.. code-block:: bash

    git clone https://github.com/lliendo/Radar.git
    cd Radar-Checks
    nosetests


License
-------

Radar is distributed under the `GNU LGPLv3 <https://www.gnu.org/licenses/lgpl.txt>`_ license.


Acknowledgments
---------------

* To `Ricardo Maia <https://openclipart.org/user-detail/ricardomaia>`_ for its wonderful Radar Openclipart logo.
* To John Curley for reviewing the english version of the documentation.


Authors
-------

* Lucas Liendo.
