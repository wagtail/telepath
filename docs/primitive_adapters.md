# Packing objects to primitive values

In some cases, rather than writing a custom JavaScript class to correspond to a Python object, it's more appropriate for the JavaScript representation to be a primitive value such as a number or string. For example, Django's [lazy translatable string objects](https://docs.djangoproject.com/en/stable/topics/i18n/translation/#lazy-translations) behave as strings for the most part, but contain custom Python-side logic to ensure that the correct translation for the active locale is chosen. This logic is not relevant to client-side code, and so it is appropriate for the JavaScript code to receive that object as a plain string. (In fact, telepath has built-in recognition for lazy translation strings; however, other Python code may use a similar mechanism and need special treatment.)

For this purpose, telepath provides the classes StringAdapter (for string values) and BaseAdapter (for other simple types) which can be subclassed, and registered in the same way as the adapters we saw previously. For example, if our Python code defines a class for managing capitalised strings:

```python
class StringLike():
    def __init__(self, val):
        self.val = val.upper()

    def __str__(self):
        return self.val
```

we can define and register an adapter that will return plain strings when unpacked on the JavaScript side, as follows:

```python
from telepath import StringAdapter, register


class StringLikeAdapter(StringAdapter):
    def build_node(self, obj, context):
        return super().build_node(str(obj), context)


register(StringLikeAdapter(), StringLike)
```

Note that the first argument passed to `super().build_node` must be of the correct type - a string for `StringAdapter`, or any JSON-serializable value for `BaseAdapter`.
