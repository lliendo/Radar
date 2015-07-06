Configuration
-------------

    Radar is simple and flexible in the way it defines different kind of
    components (checks, contacts and monitors). It uses YAML for all of
    its configuration. It was chosen among XML and JSON because is clearer
    and simpler to understand.

    When Radar starts it expects a main configuration file (this applies
    to both client and server). From that configuration file, further
    locations are read to find checks, contacts, monitors and plugins.
