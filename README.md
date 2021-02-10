# telepath

*telepath* is a Django library for exchanging data between Python and JavaScript, allowing you to build apps with rich client-side interfaces while keeping the business logic in server-side code.

## What does it do?

It provides a mechanism for packing structured data, including Python objects, into a JSON-serializable format. This mechanism can be extended to support any Python class, by registering the class with a corresponding JavaScript implementation. The packed data can then be included in an HTTP response, and unpacked in JavaScript to obtain an equivalent data structure to the original. Think of it as [`pickle`](https://docs.python.org/3/library/pickle.html), but with the unpickling happening in the browser.

Full documentation: https://wagtail.github.io/telepath/
