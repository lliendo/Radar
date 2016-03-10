Checks development
==================

In this section we will explain how checks should be developed and how Radar
runs them. As stated before checks can be programmed in your favourite
language.


Introduction
------------

Checks are the way Radar monitors any given resource. Radar only cares
how you return the output of your checks, it will expect a valid `JSON <https://en.wikipedia.org/wiki/JSON>`_ 
containing one or more of the following fields :

* status : This field is mandatory. It must be equal to any of the following
  string values : OK, WARNING, SEVERE or ERROR.

* details : This is an optional field. You can add details about how your
  check performed. Radar expects this value to be a string.

* data : This is an optional field. You can put here any data related to your
  check. Radar does not expect any particular format for this field.

So, let's assume you have an uptime check. So the minimum output for this
check would be the following JSON :

.. code-block:: javascript

    {"status": "OK"}

Radar is case insensitive when it reads a check's output so it does not care
how you name the fields (as long as you include them Radar won't complain),
so this JSON is also valid :

.. code-block:: javascript

    {"Status": "Ok"}

Any other combination of upper and lower characters is also valid. Now
suppose you want to be more verbose on this check, then you might want to
add some details :

.. code-block:: javascript

    {
        "status": "OK",
        "details": "0 days 6 hours 58 minutes"
    }

Details will be stored (along with status and data) in their respective
checks on the server side, and all your plugins will have visibility on
these fields. Now, let's assume that your check also returns data to be
processed by any of the plugins on the server side, so your JSON might
look something like this :

.. code-block:: javascript

    {
        "status": "OK",
        "data": {
            "uptime": 25092, 
            "name": "uptime"
        },
        "details": "0 days 6 hours 58 minutes"
    }

As mentioned before, there is no specific format that you have to comply
on the data field, is completely up to you how to lay it out. You can include
as much data as you want and in any desired way.


Guidelines
----------

Currently Radar checks are executed sequentially, that is one after the
other (this is expected to change on a future release), so some care must
be taken when developing them. Here are some tips and advices on how to
write good checks :

* The order of the checks execution is irrelevant. That means that check Y
  must not depend on previous execution of check X.

* Checks should check one and only one resource. If you're checking the load
  average, then just check that and not other things like free memory or
  disk usage. For those write 2 other checks.

* Checks should run as fast as possible or fail quickly. As checks run
  sequentially if one check lasts 10 seconds to complete, then subsecuent
  checks will begin executing after 10 seconds.
  
  Always fail fast if the resource you're checking is not available for
  any reason. For example if you're checking the status of your favourite
  SQL engine and for whatever reason is not running or does not allow you
  to get its status, then return an ERROR status explaining the reason and
  don't keep retrying to get its status over and over again.

* Checks should be platform independent. It is nice to just write a check
  once and then have it running on as many platforms as possible.
  This promotes reusability.

* Test your checks ! You're encouraged to write unit tests on all of your
  checks. This way you make sure that checks behave and fail as expected.


Language interpreted checks
---------------------------

If you're on Unix systems and you're planning to use any interpreted programming language
for check development keep in mind NOT to use the env program as `shebang <https://en.wikipedia.org/wiki/Shebang_%28Unix%29>`_,
for example if you were going develop a `Ruby <https://en.wikipedia.org/wiki/Ruby_%28programming_language%29>`_ script, don't use :

.. code-block:: bash

    #!/usr/bin/env ruby


If you do so, when Radar spawns the script it will end up as a defunct process.
This is because the env program is fired initially (which in turn should call
the Ruby interpreter). Always use a shebang that points directly to the interpreter
that you want to use :

.. code-block:: bash

    #!/usr/bin/ruby


On Unix systems the exact path to the interpreter that you want to use can be
retrieved using the 'whereis' command. For example to get the full path to the
Ruby interpreter you would issue :

.. code-block:: bash

    whereis ruby


The above explained only applies to Unix environments. Also remember to turn on
the execution bits if using a shebang.


Examples
--------

If you're looking for some real examples you can take a look at this  `repository <https://github.com/lliendo/Radar-Checks>`_.
In there you'll will find some basic but useful checks (written in Python) that
allows you to monitor :

* Disk usage.
* Ram usage.
* Uptime.
* Process status.

They have been designed to run on as many platforms as possible. They rely
on the excellent `psutil <https://github.com/giampaolo/psutil>`_ module.
