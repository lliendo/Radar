Checks development
------------------

    In this section we will explain how checks should be developed
    and how Radar runs them. As stated before checks can be programmed
    in your favourite language. Radar only carse how you return the
    output of your checks. Radar will only require that any check complies
    with a certain output format, in particular Radar will expect the
    output of your check to be a valid JSON containing one or more of the
    following fields :

    * status : This field is mandatory and must be equal to any of the
      following values : OK, WARNING, SEVERE or ERROR.

    * details : This is an optional field. You can add details
      about how your check performed. Radar expects this value to
      be a string.

    * data : This is an optional field. You can put here any data
      related to your check. Radar does not expect any particular
      format for this field.

    So, let's assume you have a load average check. So the minimum output
    for this check it would be the following JSON :

    .. code-block:: javascript

        {"status": "OK"}

    Radar does not care about how you name the fields (as long as you
    include them Radar won't complain), so this JSON is also valid :

    .. code-block:: javascript

        {"Status": 'Ok"}

    Any other combination of upper and lower characters is also valid.
    Now suppose you want to be more verbose on the check, then you might
    want to add some details :

    .. code-block:: javascript

        {
            "status": "WARNING",
            "details": "Load average is : 4.21 2.10 1.00"
        }

    Details will be stored (along of course with status and data) in the
    respective check on the server side, and all your plugins will have
    visibility on these fields. So now, let's assume that your check also
    returns data to be processed by any of the plugins on the server side,
    now your JSON might look something like :

    .. code-block:: javascript

        {
            "status": "OK",
            "details": "Load average is : 1.51 0.45 0.23",
            "data": {
                "1_min": 1.51,
                "5_min": 0.45,
                "15_min": 0.23
            }
        }

    As mentioned before, there is no specific format that you have to comply
    on the data field, is completly up to you how to lay it out. You can
    include as much data as you want and in any desired way.

    Currently Radar checks are executed secuentially, that is one after the
    other (this is expected to change on future releases), so some care must
    be taken when developing them. Here are some tips and advices on how to
    write good checks :

    * The order of the checks are irrelevant and your checks are independent
      of the order of execution. That means that check X must not depend
      on previous execution of check Y.

    * Checks should only check one and only one resource. If you're checking
      the load average, then just check that and not other things like
      free memory or disk usage. For those write 2 other checks.

    * Checks should run as fast as possible or fail quickly. As checks run
      sequentially if one check lasts 10 seconds to complete, then subsecuent
      checks will begin executing after 10 seconds.
      
      Always fail fast if the resource you're checking is not available for
      any reason. For example if you're checking the status of your favourite
      SQL engine and is not running or does not allow you to get its status,
      then return an ERROR status explaining the reason.

    * Checks should be platform independent. It is nice to just write once
      a check and then have it running on as much platforms as possible.

    * Test your checks. You're encouraged to write unit tests on all of
      your checks. This way you make sure that checks behave and also
      fail as expected.
