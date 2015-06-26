
TODO
----

    * Make this prototype serious = Add tests !
    * Implement basic security countermeasures. Server & client sides.
    * Support name resolution for listen/connect options from server/client.
    * Implement message compression (if payload is greater than MAX_PAYLOAD_SIZE).
      Split the message if compressed payload is greater than MAX_PAYLOAD_SIZE.
    * Remote Control console.
    * Last but not least write docs !
    * Distribution ?


Roadmap
-------

    * IO completion ports support (PyWin32) for Windows platforms.
    * Forward & backward compatibility (Python versions). Test on which versions
      of Python the project works.
    * Add further OS support. Oracle Solaris. Other propietary OSes ?
    * Minimum plugins & checks library.
      Plugins : At least an EmailNotifier / SSLEmailNotifier.
      Checks : CPU, RAM, Disks.
    * Build an abstract class that makes it easy build checks from Python.
    * Add secure TCP connections (using TLS/SSL sockets).
    * SNMP support ? We should !
    * UDP support ?
    * Add passive checks (requires UDP support !).
    * Add IPv6 support !
    * Responsive web interface. This is a completly separate project by its own.
