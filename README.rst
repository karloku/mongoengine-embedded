|PyPI version|\ |Build Status|

====================
mongoengine-embedded
====================

This package provides basic CRUD methods on EmbeddedDocumentListField
through \_id.

Usage
-----

.. code:: python

    import mongoengine
    from mongoengine_embedded import EmbeddedResource, ResourceContainer

    # embedded resource
    class Masterpiece(mongoengine.EmbeddedDocument, EmbeddedResource):
        title = mongoengine.StringField()

    # document contains embedded resource
    @ResourceContainer
    class Monkey(mongoengine.Document):
        masterpieces = mongoengine.EmbeddedDocumentListField(
            Masterpiece, element_name='masterpiece')

    the_monkey = Monkey()
    the_monkey.save()

    # Create
    one_masterpiece = the_monkey.create_masterpiece(title='Complete Works of William Shakespeare')
    another_masterpiece = the_monkey.create_masterpiece(title='Siku Quanshu')

    another_id = another_masterpiece.id
    # Read
    another = the_monkey.get_masterpiece_by_id(another_id)

    # Update
    the_monkey.modify_masterpiece_by_id(another_id, set__name='Jing Shi Zi Ji')

    # Destroy
    the_monkey.destroy_masterpiece_by_id(another_id)

Installation
------------

This Package can be installed through pip:

.. code:: bash

    pip install mongoengine-embedded

LICENSE
-------

`MIT LICENSE <LICENSE>`_

.. |PyPI version| image:: https://badge.fury.io/py/mongoengine-embedded.svg
   :target: https://badge.fury.io/py/mongoengine-embedded
.. |Build Status| image:: https://travis-ci.org/karloku/mongoengine-embedded.svg?branch=master
   :target: https://travis-ci.org/karloku/mongoengine-embedded
