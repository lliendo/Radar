TODO
----

    * Support name resolution for listen/connect options from server/client.
    * Implement message compression (if payload is greater than MAX_PAYLOAD_SIZE).
      Split the message if compressed payload is greater than MAX_PAYLOAD_SIZE.
    * Remote Control console.
    * Distribution ?


Roadmap
-------

    * Forward & backward compatibility (Python versions). Test on which versions
      of Python the project works.
    * Add optional secure TCP connections (using TLS/SSL sockets).
    * SNMP support ? We should !
    * UDP support ?
    * Add passive checks (requires UDP support ?).
    * Add IPv6 support !
    * Responsive web interface. This is a completly separate project by its own.
