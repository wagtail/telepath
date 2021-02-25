# Data format

The data format used internally by telepath allows arbitrary objects to be represented as JSON-serialisable data structures. Data is unpacked by recursively descending the JSON-parsed data structure; certain dict (object) values are designated as special cases by the presence of any of the following reserved key names: `"_type"`, `"_args"`, `"_id"`, `"_ref"`, `"_dict"`, `"_list"`, `"_val"`. Arrays, and dict values that do not contain any reserved key names, are handled by recursively unpacking their child elements; all other values (strings, numbers, booleans and `null`) are left unchanged.

The reserved key names have the following meanings:

## `_type`

Represents an object that needs to be instantiated using a constructor function. The value of `_type` is a string identifier for a constructor function that has been registered with `telepath.register`. This dict will also have an `_args` item giving a list of arguments to be passed to the function; values in this list will be recursively unpacked before being passed to the constructor.

For example, if the function (or class) `Dog(name, breed)` has been registered with `telepath.register('myproject.animals.Dog', Dog)`, then the dict

    {"_type": "myproject.animals.Dog", "_args": ["Lassie", "collie"]}

will be unpacked to the result of `new Dog("Lassie", "collie")`.

## `_id`

Assigns a numeric identifier to the unpacked object, to be referenced elsewhere using `_ref`; this allows one object instance to appear multiple times in the unpacked data structure.

## `_ref`

Represents an object that has been defined elsewhere in the data structure and assigned an identifier via `_id`. For example, if the function `Kennel(allDogs, dogsByName, dogsByBreed)` has been registered under the name `myproject.homes.Kennel`, then the dict:

    {"_type": "myproject.homes.Kennel", "_args": [
        [{"_type": "myproject.animals.Dog", "_args": ["Lassie", "collie"], "_id": 1}],
        {"Lassie": {"_ref": 1}},
        {"collie": {"_ref": 1}}
    ]}

will be unpacked by first evaluating `new Dog("Lassie", "collie")` as above, then passing that same object instance in all three arguments of `Kennel`. Note that forward references are valid; `_ref` may reference an `_id` identifier that appears later in the serialised data stream.

## `_dict`

Represents a dict (object) value. For example:

    {"_dict": {"a": 1, "b": 2}}

is equivalent to `{"a": 1, "b": 2}`. As with the short form, values in the dict will be unpacked recursively. In practice, the long-form `_dict` representation will be used in one of two situations:

* When the dict keys include reserved names that should be handled literally: for example, `{"_dict": {"_name": "Lassie", "_type": "collie"}}` will evaluate to the dict `{"_name": "Lassie", "_type": "collie"}` and not attempt to interpret `"_type": "collie"` as a constructor function.
* When an `_id` identifier needs to be attached to the dict: for example, a dict defined as `{"_dict": {"a": 1, "b": 2}, "_id": 2}` can be referenced elsewhere as `{"_ref": 2}`.

## `_list`

Represents a list (array) value. For example:

    {"_list": [1, 2, 3]}

is equivalent to `[1, 2, 3]`. As with the short form, elements in the list will be unpacked recursively. In practice, the long-form `_list` representation will only be used when an `_id` identifier needs to be attached to it: for example, a list defined as `{"_list": [1, 2, 3], "_id": 3}` can be referenced elsewhere as `{"_ref": 3}`.

## `_val`

Represents a primitive value that does not need to be expanded further. For example:

    {"_val": "hello world"}

is equivalent to `"hello world"`. In practice, the long-form `_list` representation will only be used when an `_id` identifier needs to be attached to it: for example, a string defined as `{"_val": "hello world", "_id": 4}` can be referenced elsewhere as `{"_id": 4}`.
