Objson
======

The package :mod:`json` is used to serialize and deserialize json object. The :func:`json.loads`
function return dict object which represent the json object, I think the ``[key]`` operator,
especially the json object contains hierarchical project. So, SimpleKit provides
some simple and brief way which operate the object object.

Loads json
-------------

Objson provides the same interface with :mod:`json` package, the example code:

.. code-block:: python

    from simplekit import objson
    text = r'{"Name": "benjamin", "age": 27, "marriage":True}'
    obj = objson.loads(text)

    assert obj is not None
    assert obj.Name == 'benjamin'
    assert obj['Name'] == 'benjamin'
    assert obj.age == 27
    assert obj['age'] == 27
    assert obj.marriage


Notice,  :func:`objson.loads` return a object represent the json object. and you
can access the json property by ``.`` operator, like: ``assert obj.age == 27``,
and  the ``[key]`` operator is available.

Dumps json
-------------

The ``dumps`` function is the some as :func:`json.dumps`, just can support dumps the object
which deserialized by :func:`json.loads`.  the example code:

.. code-block:: python

    from simplekit import objson
    obj = {'Name': 'Wendy', 'age':27}
    text = objson.dumps(obj)
    obj2 = objson.loads(text)
    text2 = objson.dumps(obj2)

    assert text == text2

Notice
--------
If the JSON property name is one of the below:

and, as, assert, break, class, continue, def, del, elif, else,
except, exec, finally, for, from, global, if, import, in, is,
lambda, not, or, pass, print, raise, return, try, while, with,
yield

Or

the property name is start with digit,

the dolphin libs will escape the property, add prefix string "m".

and also, property contains any other character which is not alpha, digit and ``_`` (underscore)
will replace to ``_`` (underscore).

For example:

.. code-block:: python

    text = r'{"class": true, "from-cookie": true, "0file":True}'
    obj = dolphin.loads(text)

    assert obj.mclass
    assert obj['class']
    assert obj.from_cookie
    assert obj['from-cookie']
    assert obj.m0file
    assert obj['0file']
