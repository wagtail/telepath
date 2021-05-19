# Packing objects from external packages

Sometimes it may be necessary to pack objects that are defined by the Python standard library or a third-party package such as Django. In this case, adding a `telepath_pack` method as described earlier is not an option, since the class definition exists outside of your own code. To accommodate this, telepath allows you to define the packing logic in an `Adapter` object, and register this so that it is used whenever an object of the given type is encountered.

For example, suppose we want to be able to pack [`datetime.time`](https://docs.python.org/3/library/datetime.html#time-objects) instances. This can be done as follows:

```python
import datetime
from telepath import Adapter, register


class TimeAdapter(Adapter):
    def pack(self, obj, context):
        context.add_media(js='datetime.js')
        return ('datetime.Time', [obj.hour, obj.minute, obj.second])


register(TimeAdapter(), datetime.time)
```

The `pack` method here works in the same way as a `telepath_pack` method on the class itself, except that the object is passed as an argument rather than operating on `self`. The resulting `TimeAdapter` object is then passed to `register` to be used for `datetime.time` instances.

On the JavaScript side, the `datetime.Time` constructor can then be defined and registered in the same way as before. In `datetime.js`:

```javascript
class Time {
    constructor(hour, minute, second) {
        this.hour = hour;
        this.minute = minute;
        this.second = second;
    }

    toString() {
        return (
            this.hour.toString().padStart(2, '0')
            + ':' + this.minute.toString().padStart(2, '0')
            + ':' + this.second.toString().padStart(2, '0')
        );
    }
}
window.telepath.register('datetime.Time', Time);
```
