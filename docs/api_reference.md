# API reference

## Python API

### `telepath.Adapter()`

Base class for an adapter object, which defines how telepath should handle a particular Python type. Subclasses should define the following:

* `js_constructor` - The identifier for a JavaScript constructor function that will be registered with the JavaScript `register` method; this constructor function will be called when an object of this type is encountered in the data. This identifier should be unique among all adapter objects registered; it is recommended to use a namespaced string with dots as separators (e.g. `'myproject.animals.Cat'`).
* `js_args(obj)` - Given the object to be packed, return the list of arguments that should be passed to the constructor function to recreate the corresponding client-side object. The arguments must themselves be telepath-packable values (i.e. basic JSON-serialisable types, or objects with a telepath adapter defined).
* `get_media(obj)` - Given the object to be packed, return a [Django form media object](https://docs.djangoproject.com/en/stable/topics/forms/media/) for the JavaScript and CSS assets needed to unpack the client-side object. This should include the .js file where the constructor function is defined and registered with telepath. Alternatively, if the media definition is the same for all object instances, this can be defined as an inner `Media` class.

### `telepath.register(adapter, cls)`

Registers an adapter object (an instance of a `telepath.Adapter` subclass) to be used by telepath when it encounters an object of type `cls`. If more than one class in an object's inheritance chain has an adapter defined, the most specific one according to the method resolution order (MRO) will be used.

### `telepath.JSContext()`

An object for handling all packing operations for a particular request. Provides the following methods and attributes:

* `pack(obj)` - Returns the packed representation of the given object. This representation is a value that can be serialised as JSON and included in an HTTP response; on the client side this can then be deserialised with `JSON.parse` and passed to `telepath.unpack` to obtain the unpacked object.
* `media` - A [Django form media object](https://docs.djangoproject.com/en/stable/topics/forms/media/) listing the JavaScript and CSS assets needed to unpack all objects that have been passed to `pack`. This object should be rendered into a template response to ensure that the client-side `telepath.unpack` operation has all the necessary definitions.

### `telepath.AdapterRegistry(telepath_js_path='telepath/js/telepath.js')`

An object that manages a set of adapter objects to be used collectively for packing values. Normally you will not need to work with this class directly, as the telepath module maintains a global set of adapters that are registered with the top-level `register` function and used by `JSContext`; however, in some cases it may be useful to build a 'local' registry of adapters with different behaviour from the global set, such as serving media from a custom application-specific path. Provides the method `register(adapter, cls)` which is equivalent to the top-level `register` function, and the property `js_context_class` which returns a class equivalent to `JSContext` that uses this local registry when packing values. The optional `telepath_js_path` argument specifies the path to `telepath.js` to be used in this object's media definitions.


## JavaScript API

### `window.telepath`

An object that manages unpacking values. Provides the following methods:

* `register(name, constructor)` - Registers a constructor function to be used when unpacking. The `name` argument should match the identifier given as `js_constructor` for an adapter object.
* `unpack(val)` - Unpacks the packed telepath data representation into a native JavaScript object.
