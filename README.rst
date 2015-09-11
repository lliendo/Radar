
Radar Monitoring System
=======================

Radar is general purpose monitoring system. It aims to be simple and extendable.
It uses arbitrary check execution and server side plugins to provide flexibility.
It is entirely written in the Python programming language and is distributed
under the LGPL v3 license.


Status
------

Radar is currently in ALPHA status, however its foundations are complete.
You can take a look at the TODO.rst to have an idea what features are going to
(or might) be implemented in the future.


Documentation
-------------

You can read how to setup and use Radar (both client and server) from `here <https://...>`.
You can also generate the documentation of the project by yourself using `Sphinx <http://sphinx-doc.org/>`.
You will have to install Sphinx in first place :

.. code-block:: bash

    pip install sphinx


Now change to the project's documentation directory and run make html :

.. code-block:: bash

    cd Radar/docs
    make html


Sphinx will output the generated documentation to the '_build' directory. To read
the generated docs open up a browser and then load the index.html file. Currently
documentation is only available in English and Spanish languages.

If you think that documentation is incomplete or not clear enough, please let
me know.


Supported platforms
-------------------

Radar should run without any problems in any platform where the Python interpreter
is supported.


Installation
------------

Always the latest release is available from PyPI. To install simply run :

.. code-block:: bash

    pip install radar-monitoring-system


If you wish however to use the latest version from this repository :

.. code-block:: bash

    git clone https://github.com/lliendo/Radar.git
    cd Radar
    python setup.py install


Development
-----------

If you're interested in how Radar works you are encouraged to take a look at
the code, documentation about its internals can be found `here <https://...>`.
Radar is designed to be both simple and easy to use and understand.


Tests
-----

Radar uses `Tox <https://...>` to run its tests. To run the Radar's tests install
Tox and then run :

.. code-block:: bash

    git clone https://github.com/lliendo/Radar.git
    cd Radar
    tox


License
-------

Radar is distributed under the LGPL v3 license.


Contact
-------

If you find this software useful you can drop me a line. Bug reporting, suggestions,
missing documentation and critics (both positive and negative) of any kind are
always welcome !


Authors
-------

    * Lucas Liendo.
