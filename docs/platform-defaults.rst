Platform defaults
=================

    Radar supports all platforms where the Python interpreter is able to run.
    However, Radar internally makes distinction between UNIX alike OSes and
    Microsoft Windows platforms.


UNIX OSes
---------

    For UNIX OSes these default values are used :

    Radar server (/etc/radar/server/main.yml) :

    .. code-block:: yaml

        listen:
            address: localhost
            port: 3333

        run as:
            user: radar
            group: radar

        log:
            to: /var/log/radar-server.log
            size: 100
            rotations: 5

        pid file: /var/run/radar-server.pid
        polling time: 300
        checks: /etc/radar/server/config/checks
        contacts: /etc/radar/server/config/contacts
        monitors: /etc/radar/server/config/monitors
        plugins: /usr/local/radar/server/plugins


    Radar client (/etc/radar/client/main.yml) :

    .. code-block:: yaml

        connect:
            to: localhost
            port: 3333

        run as:
            user: radar
            group: radar

        log:
            to: /var/log/radar-client.log
            size: 100
            rotations: 5

        pid file: /var/run/radar-client.pid
        checks: /usr/local/radar/client/checks
        enforce ownership: True
        reconnect: True


Microsoft Windows platforms
---------------------------

    Microsoft Windows platforms have the following default values :

    Radar server (C:\\Program Files\\Radar\\Server\\Config\\main.yml) :

    .. code-block:: yaml

        listen:
            address: localhost
            port: 3333

        log:
            to: C:\Program Files\Radar\Log\radar-server.log
            size: 100
            rotations: 5

        polling time: 300
        checks: C:\Program Files\Radar\Server\Config\Checks
        contacts: C:\Program Files\Radar\Server\Config\Contacts
        monitors: C:\Program Files\Radar\Server\Config\Monitors
        plugins: C:\Program Files\Radar\Server\Config\Plugins


    Radar client (C:\\Program Files\\Radar\\Client\\Config\\main.yml) :

    .. code-block:: yaml

        connect:
            to: localhost
            port: 3333

        log:
            to: C:\Program Files\Radar\Log\radar-client.log
            size: 100
            rotations: 5

        checks: C:\Program Files\Radar\Client\Config\Checks
        reconnect: True
