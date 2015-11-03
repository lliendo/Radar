Limitations
===========

Radar is a brand new project and here are some things that you should know
about its current status :

* Concurrent checks : Radar does not support concurrent check execution
  at the moment.

* Concurrent plugin execution : At the moment all plugins are executed
  sequentially, this is in a way identical to the checks limitation described
  above.

* Passive checks : There's no passive check support yet. This feature will
  certainly be implemented in the near future.

* SNMP checks : SNMP is not supported. It hasn't been yet defined if this
  feature will be supported at all.

* SSL/TLS : Is not yet supported but certainly it's going to be included on
  a future release.

* IPv6 addresses are not supported yet.

* Both Windows client and server need to be improved considerably.
  I/O Completion Port support has been developed but is not working properly,
  consequently Radar relies on the inefficient select system call.


These limitations are intended be overcomed as the project evolves. Currently
Radar's status is ALPHA and proper and expected behaviour needs to be assured
before moving to further features. Also minor changes can be expected at
this stage.
