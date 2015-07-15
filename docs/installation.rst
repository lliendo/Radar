Installation
============

    You can install Radar either using pip or manually from the latest
    version from Github. If you want to use pip :

    .. code-block:: bash

        pip install radar-monitoring-system

    If you want to manually install the latest version from Github
    (you will need `GIT <https://git-scm.com/>`_ installed on your system) then open a terminal and run :

    .. code-block:: bash

        git clone https://github.com/lliendo/Radar.git
        cd Radar
        python setup.py install


Checking the installation
-------------------------

    You can check that Radar was successfully installed by running from the
    command line :

    .. code-block:: bash

        radar-client -v
        radar-server -v

    This will display the current version of Radar (client and server)
    installed on your system. If you see these versions then you got both
    client and server successfully installed, otherwise something went wrong.

    By default Radar expects to find configuration files in well-defined
    places. These directories are platform dependant so you may want to take
    a look at the default places where those files should be found depending
    on the platform where Radar is running :

        * GNU/Linux :

        * FreeBSD :

        * NetBSD :

        * OpenBSD :

        * Darwin / Mac OS X :

        * Microsoft Windows :

    It is a good practice to use these default directories. Of course if
    don't want to use those locations you can change them from the main
    configuration file.

    Radar only takes its main configuration file to be able to run. 
    If you want to override the default main configuration file path
    you can invoke Radar this way :

    .. code-block:: bash

        radar-client -c ALTERNATE_PATH_TO_MAIN_CONFIGURATION_FILE
        radar-server -c ALTERNATE_PATH_TO_MAIN_CONFIGURATION_FILE

    The -c option specifies an alternate main configuration file.
