Platform defaults
=================

    Radar supports all platforms where the Python interpreter is able to run.
    However, Radar internally makes distinction between UNIX alike OSes
    and MS Windows platforms.

    For UNIX alike OSes these default values are used :

    Radar server :

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


    Radar client :

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


    MS Windows platforms have these default values :

    Radar server :


    Radar client :


