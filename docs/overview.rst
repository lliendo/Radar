Overview
========

    Radar is a monitoring tool that tries to make things simple and easy. Radar
    is not an advanced monitoring tool and you may not find all features that
    you may find in other monitoring solutions, however Radar's philosophy relies
    heavily on these two ideas :

        * Simplicity : Both user-interface and source code are intended to be
          as simple as possible. The code isn't designed to grow indefinetly mainly
          because its behaviour can be better controlled and tested. The code is
          designed to be easy to understand and modify. Its main ideas are
          described in the internals section of this document to make it easy
          anyone play with the code.

        * Extendability : As you will see later Radar is not focused on any
          particular resource monitoring. Instead it allows you to easily
          integrate any custom designed checks to verify any resource that you
          want. This does not only applies to IT infratructure, you could get
          for example data from a sensor that is attached to a PC or device that
          runs the Python interpreter.

    Once you got you Radar server up and running any number of clients may connect
    and after a user-defined interval they will be polled. The following diagram
    shows how Radar operates :



    So what can you really do with Radar ? Here are some ideas :

        * Notifications : This is a typical use. Notify any of your defined contacts
          if something is not performing as expected. You can notify by email, sms
          or maybe put data in a queue and have another process to take that
          responsibility.

        * Graphing tool : Each time you receive data from a check you can add that
          information to a database (like `RRDtool <http://www.rrdtool.org>`_) a then generate graphs.
          You can get this way trends of your resources.

        * Take an advanced action : Suppose that you run a cluster of servers on
          a cloud-based provider. Then by inspecting the replies of your checks,
          you can write a plugin to add/remove servers on demand, if you get for
          example that the amount of requests/sec. that a server is processing
          are exceeded.
          Another potential use is to take a remote action on a host if certain
          condition is met.

    Any of these uses requires that you write a plugin for it. Remember that
    Radar does not include any built-in functinality and these tasks are
    delegated to plugins. You can take a look how to develop checks and plugins
    on the following sections of this document. Don't panic ! A lot of effort
    has been put to make these tasks as easy as possible, so keep reading the
    docs.
