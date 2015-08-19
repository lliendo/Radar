Radar internals
===============

    Radar has been carefully designed to its keep base code clean and understandable,
    so everyone can take a look at its internals (and hopefully people play
    around with the code).


Design
------

    Radar is designed to be a small tool, its core isn't intended to grow
    indefinetly besides some currently lacking features. The reason behind
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
    intends to be self-describing. Radar strictly tries to stick to this rule.


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


Class diagrams
--------------

    We're now going to take a look at the most relevant classes that Radar (both
    client and server) has.

    The main idea of these diagrams is to give you the big picture on how different
    classes are related each other and how objects talk between them.


Initialization
--------------

    Both Radar client and server go through almost the same steps before going
    into operational mode. When Radar (client or server) is fired up it 
    instantiates a launcher (RadarClientLauncher for the client and
    RadarServerLauncher for the server) and inmediatly calls its run() method.

    From that point a three phase initialization takes place :

    1 - First the command line is processed. This is done in the RadarLauncher
        class. After this objects and configurations are read from the main
        configuration file and alternate files in the case of the server.
    
    2 - Client and server proceed to define main, create and configure threads. 
    3 - Finally threads are launched.

    After all threads are successfully launched client and server break away and
    start performing different tasks.


Server operation
----------------


Client operation
----------------


Threads
-------

    Both Radar client and server make use of threads to perform concurrent tasks.
    Radar server consists of three threads :

    Radar client is designed around two threads :
