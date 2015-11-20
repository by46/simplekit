Objson
======

The package ``json`` is used to serialize and deserialize json object. The ``json.loads(s)``
function return dict object which represent the json object, I think the ``[key]`` operator,
especially the json object contains hierarchical project. So, SimpleKit provides
some simple and brief way which operate the object object.

Loads json
-------------

Objson provides the same interface with ``json`` package, the example code:
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


Notice, ``objson.loads(s)`` return a object represent the json object. and you
can access the json property by ``.`` operator, like: ``assert obj.age == 27``,
and  the ``[key]`` operator is available.

Dumps json
-------------

The ``dumps`` function is the some as ``json``, just can support dumps the object
which deserialized by ``objson.loads(s)``. the example code:
.. code-block:: python

    from simplekit import objson
    obj = {'Name': 'Wendy', 'age':27}
    text = objson.dumps(obj)
    obj2 = objson.loads(text)
    text2 = objson.dumps(obj2)

    assert text == text2

