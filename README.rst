
Radar Monitoring System
=======================

Radar is general purpose monitoring system. It aims to be simple and extendable.
It uses arbitrary check execution and server side plugins to provide maximum
flexibility. It is entirely written in the Pythonprogramming language and is
distributed under the LGPL v3 license.


Status
------

Radar is currently under testing and bug fixing, however its foundations are
almost complete. You can take a look at the TODO to have an idea what features
are going to (or might) be implemented in the future.


Documentation
-------------

You can read how to setup and use Radar (both client and server) from `here <https://...>`.
If you think that documentation is incomplete or not clear enough, please let
me know.


Supported platforms
-------------------

Radar tries to run on most popular platforms. Currently suported platforms include :

    * GNU/Linux.
    * FreeBSD.
    * NetBSD.
    * OpenBSD.
    * Darwin / Mac OS X.
    * Microsoft Windows (with some limited features).


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
the code, documentation about its internals are `here <https://...>`.
Radar is designed to be both simple and easy to use and understand, it will
always try to keep this way.


Tests
-----

Radar uses Travis CI to run its tests. You can however run tests manually by
cloning the latest available code (you will need to install `Tox <https://...>`) :

.. code-block:: bash

    git clone https://github.com/lliendo/Radar.git
    cd Radar
    tox


License
-------

Radar is distributed under the LGPL v3 license.


Contact
-------

If you find this software useful you can drop me a line. Bug reporting,
suggestions, missing documentation and critics of any kind are always welcome !


Authors
-------

    * Lucas Liendo.
