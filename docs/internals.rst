Radar internals
===============

    Radar has been carefully designed to its keep base code clean and understandable,
    so everyone can take a look at its internals (and hopefully people play
    around with the code).

    This section of the documentation tries to expose the main ideas that were
    implemente to make this project possible. We'll not describe every single detail
    because that would take a huge amount of time and you'll get bored. Instead
    I've decided to describe few things as possible and try to reflect why a
    decision was taken that way. Also consider that as everybody I make mistakes
    and no perfect software design exists and Radar is way way long from being
    or achieve that.


General design
--------------

    Radar is designed to be a small tool, its core isn't intended to grow
    indefinetly besides some currently feature lacking. The reason behind
    this decision is that a tool that is small and controlled in its size and
    its objectives is easier to understand and does its work better than an
    all-problem-solving solution.
    This also has a downside : a small tool may not offer advanced or complex
    features. Radar's main goal is to be a simple and easy to use tool hence the
    reason why you might not find as many features as other solutions may offer.

    Radar makes use of object oriented programming, every component is modeled
    through a class. Some few classes make use of mixins and all errors are
    handled through exceptions. Radar also makes use of comprehension lists
    extensively across the project.

    If you take a fast look through the code you'll realize that almost every
    method is only a few lines long. Every class is intended to perform a
    specific task and each method solves a concrete piece of that task.
    The result is that you won't find complex or twisted code and reading any
    piece of code to get the idea of what is doing takes only a few seconds.
    The code mostly lacks of comments, the reason for this is that the code
    intends to be self-describing. Radar tries to stick to this rule.


Project layout
--------------

    Radar has the following project structure :

    .. code-block:: bash

        /Radar
            /docs                # Includes project's documentation in reStructuredText.
                                 # Sphinx is used for documentation generation.

            /tests               # Project's tests.

            /templates           # Radar client and server templates used as
                                 # initial configurations.
            /radar
                /check           # Check and CheckGroup abstractions.
                /check_manager   # CheckManager governs check execution.
                /class_loader    # Loading mechanism for plugins.
                /client          # Main RadarClient abstraction.

                /client_manager  # ClientManager handles Radar clients when connect,
                                 # disconnect and send replies.

                /config          # Includes builders that handle initializations of
                                 # both Radar client and server.

                /contact         # Contact and ContactGroup abstractions.

                /initial_setup   # Includes facilities to configure Radar after
                                 # it has been installed.

                /launcher        # Includes classes that fire up both Radar server
                                 # and client.

                /logger          # Logging services.
                /misc            # A few helper classes mainly used by Radar server.
                /monitor         # Monitor abstraction.

                /network         # Low level network facilities to handle both 
                                 # server and clients. Different platform specific
                                 # network monitors are found here.

                /platform_setup  # Platform specific configuration and setup.

                /plugin          # Plugin and PluginManager classes work each other
                                 # closely to allow plugin functionality.

                /protocol        # Low level network protocol that Radar uses for
                                 # communicating between server and clients.
                                 
                /server          # Main RadarServer abstraction.





Initialization
--------------

    Both Radar client and server go through almost the same steps before going
    into operational mode. When Radar (client or server) is fired up it 
    instantiates a launcher (RadarClientLauncher for the client and
    RadarServerLauncher for the server) and inmediatly calls its run() method.

    From that point a three phase initialization takes place :

    1 - First the command line is processed. This is done in the RadarLauncher
        class. After this, objects and configurations are read from the main
        configuration file and alternate files in the case of the server are
        parsed and processed.
    
    2 - Client and server proceed to define, create and configure threads. 

    3 - Finally threads are launched.

    After all threads are successfully launched client and server break away and
    start performing completly different tasks.


Radar's operational design
--------------------------

    Both Radar client and server operate in an event triggered fashion and make
    use of threads to distribute the workload.
    If you look at the code of the RadarServer and RadarClient you'll find
    methods called 'on_something'. Every time a network event occurs it is
    reflected in any of those methods. The heart of Radar are two abstract
    classes : Client and Server which can be found under the network module.
    The Client and Server classes operate in a very similar way despite being
    different the way they handle network sockets.

    The network module also provides some network monitors that are platform
    dependant. Before Radar server goes into operational mode it tries to select
    the best multiplex i/o method available. In any case if the platform can't
    be detected or an efficient multiplexing method cannot be found Radar will
    keep working with a SelectMonitor (which relies on the select system call).
    The current supported multiplexing strategies are : select, poll, epoll,
    kqueue and i/o completion ports.

    Radar client and server also operate in a non-blocking way. Its main thread
    loops are iterated constantly every 200 milliseconds. This prevents any
    single client from blocking the server indefinetly due to a malformed or
    incomplete network message.


Server operation
----------------

    The main work of the server is splitted across three main threads :

    1 - RadarServer.

    2 - RadarServerPoller.

    3 - PluginManager.


    RadarServer :

    This thread is responsible for accepting clients and receiving replies from
    them. A client is only accepted if it is defined in at least one monitor
    and is not duplicated (that is, if there isn't a client already connected).
    
    Once a client is successfully accepted it is registered within the ClientManager.
    The ClientManager acts as proxy that talks directly to all defined monitors.
    Every monitor internally knows if it has to accept a client when it connects,
    if it is indeed accepted then a deep copy of the checks and contacts is stored
    along with the instance of that client. This copy is needed because more than
    one client may match against the same monitor.

    The reverse process happens when a client disconnects, the RadarServer unregisters
    that client and the connection is closed.

    When a client sends a reply is it also initially processed by the ClientManager.
    The reason for this is that we need to get a list of checks and contacts
    that are affected by such reply. These two lists of objects are later on
    sent to the PluginManager to be processed by any defined plugins.


    RadarServerPoller :

    This is the simplest thread. Every N seconds it simply asks the ClientManager
    to poll all of its monitors. The existence of this thread is that it makes
    sense to have a different abstraction that decides when its time to poll
    the clients. If this work would have been done in the RadarServer we would
    be mixing asynchronus (network activity) and synchronus (wait a certain amount
    of time) events making the overall design more complex to both understand
    and work with.


    PluginManager :

    As its name indicates, this is the place where all plugins are executed and
    controlled. Whenever the RadarServer receives a reply from a client and after
    little processing a dictionary containing all plugin data is written to a 
    queue that RadarServer and PluginManager share, this is the mechanism of
    communication between RadarServer and PluginManager.
    The PluginManager quietly waits for a new dictionary to arrive from this
    queue, when it does it disassembles all parameters and does object id
    dereferencing of two lists that contain the affected checks and the
    related contacts. This dereferencing is possible because threads share the
    same address space. This solution seems more elegant and effective than
    re-instantiating those objects from their values.
    After this pre-processing every plugin's run method is called. If a plugin
    does not work properly the exception is trapped and registered in the
    Radar's log.


Client operation
----------------


Class diagrams
--------------

    Sometimes class diagrams help you see the big picture of a design and also
    act as excellent documentation. Here are some diagrams that may help you
    to see a different picture that words can't describe or make cumbersome.
