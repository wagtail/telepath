# Tutorial

Suppose we're building a Django app for playing draughts (checkers). We've hammered away for days or weeks, building a Python implementation of the rules of the game, with classes to represent the current game state and the individual pieces. However, we also want to provide the player with a suitably friendly user interface, which means it's time for us to write a JavaScript front-end. Our UI code is inevitably going to have its own objects representing the board and playing pieces, mirroring the data structures we're keeping track of on the server - but we can't send Python objects down the wire, so getting that data onto the client will typically mean devising a JSON representation of the game state, and a whole lot of boilerplate code at either end, looping over data structures to convert to and from native objects. Let's see how telepath can streamline that process.

A full game of draughts is a bit much for a tutorial, so we'll settle for just rendering the board instead...

From a clean Python environment, create a new Django project:

```shell
pip install "Django>=3.1,<3.2"
django-admin startproject draughts
cd draughts
./manage.py startapp games
```

Add `'games',` to the INSTALLED_APPS list in `draughts/settings.py`.

To keep things simple, we won't touch the database in this example, and will represent the game state as ordinary Python classes rather than Django models. Edit `games/views.py` as follows:

```python
from django.shortcuts import render


class Piece:
    def __init__(self, color, position):
        self.color = color
        self.position = position


class GameState:
    def __init__(self, pieces):
        self.pieces = pieces

    @staticmethod
    def new_game():
        black_pieces = [
            Piece('black', (x, y))
            for y in range(0, 3)
            for x in range((y + 1) % 2, 8, 2)
        ]
        white_pieces = [
            Piece('white', (x, y))
            for y in range(5, 8)
            for x in range((y + 1) % 2, 8, 2)
        ]
        return GameState(black_pieces + white_pieces)


def game(request):
    game_state = GameState.new_game()

    return render(request, 'game.html', {})
```

Create `games/templates/game.html` as follows:

```html
<!doctype html>
<html>
    <head>
        <title>Draughts</title>
        <script>
            document.addEventListener('DOMContentLoaded', event => {
                const gameElement = document.getElementById('game');
                gameElement.innerHTML = 'TODO: render the board here'
            });
        </script>
    </head>
    <body>
        <h1>Draughts</h1>
        <div id="game">
        </div>
    </body>
</html>
```

Add the new view to `draughts/urls.py`:
```python
from django.contrib import admin
from django.urls import path

from games.views import game

urlpatterns = [
    path('', game),
    path('admin/', admin.site.urls),
]
```

Now start the server with `./manage.py runserver` and visit `http://localhost:8000/`.

So far we've created a `GameState` object representing a new game - it's now time to introduce telepath, so that we can transfer that object to the client. Run:

```shell
pip install telepath
```

and add `'telepath',` to the INSTALLED_APPS list in `draughts/settings.py`. Now edit `games/views.py`:

```python hl_lines="1 3 10-12 15"
import json
from django.shortcuts import render
from telepath import JSContext

# ...

def game(request):
    game_state = GameState.new_game()

    js_context = JSContext()
    packed_game_state = js_context.pack(game_state)
    game_state_json = json.dumps(packed_game_state)

    return render(request, 'game.html', {
        'game_state_json': game_state_json,
    })
```

Here `JSContext` is a helper that manages the conversion of our game state object into a representation we can use in Javascript. `js_context.pack` takes that object and converts it to a value that can be JSON-serialised and passed to our template. However, reloading the page now fails with an error of the form: `don't know how to pack object: <games.views.GameState object at 0x10f3f2490>`

This is because `GameState` is a custom Python type that telepath does not yet know how to handle. Any custom type passed to `pack` must be linked to a corresponding JavaScript implementation; this is done by defining an `Adapter` object and registering it with telepath. Update `games/views.py` as follows:

```python hl_lines="3 11-21"
import json
from django.shortcuts import render
from telepath import Adapter, JSContext, register

# ...

class GameState:
    # keep definition as before


class GameStateAdapter(Adapter):
    js_constructor = 'draughts.GameState'

    def js_args(self, game_state):
        return [game_state.pieces]

    class Media:
        js = ['draughts.js']


register(GameStateAdapter(), GameState)
```

Here `js_constructor` is an identifier for a JavaScript constructor function that will be used to build GameState instances on the client side, and `js_args` defines a list of arguments that will be passed to this constructor function in order to recreate a JavaScript counterpart of the given `game_state` object. The `Media` class indicates the file where the JavaScript implementation of GameState can be found, following Django's convention for [form media](https://docs.djangoproject.com/en/static/topics/forms/media/). We'll see what this JavaScript implementation looks like later - for now, we need to define a similar adapter for our `Piece` class, since our definition of `GameStateAdapter` is dependent on being able to pack Piece instances. Add the following definition to `games/views.py`:

```python hl_lines="5-15"
class Piece:
    # keep definition as before


class PieceAdapter(Adapter):
    js_constructor = 'draughts.Piece'

    def js_args(self, piece):
        return [piece.color, piece.position]

    class Media:
        js = ['draughts.js']


register(PieceAdapter(), Piece)
```

Reload the page and you'll see that the error has gone, indicating that we have successfully serialised the GameState object to JSON and passed it to the template. We can now include this in the template - edit `games/templates/game.html`:

```html hl_lines="3"
    <body>
        <h1>Draughts</h1>
        <div id="game" data-game-state="{{ game_state_json }}">
        </div>
    </body>
```

Reload the page again and inspect the `game` element in your browser's developer tools (in Chrome and Firefox, right-click the TODO note and select Inspect or Inspect Element), and you'll see the JSON representation of the GameState object, ready to be unpacked into a full-fledged JavaScript object.

Along with packing data into JSON-serialisable form, the `JSContext` object also keeps track of the JavaScript media definitions that will be needed to unpack the data, as its `media` property. Let's update our `game` view to pass this to the template too - in `games/views.py`:

```python hl_lines="10"
def game(request):
    game_state = GameState.new_game()

    js_context = JSContext()
    packed_game_state = js_context.pack(game_state)
    game_state_json = json.dumps(packed_game_state)

    return render(request, 'game.html', {
        'game_state_json': game_state_json,
        'media': js_context.media,
    })
```

Add this to the HTML header in `games/templates/game.html`:

```html hl_lines="3"
    <head>
        <title>Draughts</title>
        {{ media }}
        <script>
            document.addEventListener('DOMContentLoaded', event => {
                const gameElement = document.getElementById('game');
                gameElement.innerHTML = 'TODO: render the board here'
            });
        </script>
    </head>
```

Reloading the page and viewing source, you'll see that this brings in two JavaScript includes - `telepath.js` (the client-side telepath library, which provides the unpacking mechanism) and the `draughts.js` file we specified in our adapter definitions. The latter doesn't exist yet, so let's create it - in `games/static/draughts.js`:

```javascript
class Piece {
    constructor(color, position) {
        this.color = color;
        this.position = position;
    }
}
window.telepath.register('draughts.Piece', Piece);


class GameState {
    constructor(pieces) {
        this.pieces = pieces;
    }
}
window.telepath.register('draughts.GameState', GameState);
```

The two class definitions implement the constructor functions that we declared earlier in the adapter objects - the arguments received by the constructor are the ones defined by `js_args`. The `window.telepath.register` lines attach these class definitions to the corresponding identifiers that were specified through `js_constructor`. This now gives us everything we need to unpack the JSON - back in `games/templates/game.html`, update the JS code as follows:

```html hl_lines="4-8"
        <script>
            document.addEventListener('DOMContentLoaded', event => {
                const gameElement = document.getElementById('game');
                const gameStateJson = gameElement.dataset.gameState;
                const packedGameState = JSON.parse(gameStateJson);
                const gameState = window.telepath.unpack(packedGameState);
                console.log(gameState);
            })
        </script>
```

You may need to restart the server to pick up the new `games/static` folder. Reload the page, and in the browser console you should now see the `GameState` object, populated with `Piece` objects. We can now proceed to fill in our rendering code in `games/static/draughts.js`:

```javascript hl_lines="7-14 24-46"
class Piece {
    constructor(color, position) {
        this.color = color;
        this.position = position;
    }

    render(container) {
        const element = document.createElement('div');
        container.appendChild(element);
        element.style.width = element.style.height = '24px';
        element.style.border = '2px solid grey';
        element.style.borderRadius = '14px';
        element.style.backgroundColor = this.color;
    }
}
window.telepath.register('draughts.Piece', Piece)


class GameState {
    constructor(pieces) {
        this.pieces = pieces;
    }

    render(container) {
        const table = document.createElement('table');
        container.appendChild(table);
        const cells = [];
        for (let y = 0; y < 8; y++) {
            let row = document.createElement('tr');
            table.appendChild(row);
            cells[y] = [];
            for (let x = 0; x < 8; x++) {
                let cell = document.createElement('td');
                row.appendChild(cell);
                cells[y][x] = cell;
                cell.style.width = cell.style.height = '32px';
                cell.style.backgroundColor = (x + y) % 2 ? 'silver': 'white';
            }
        }

        this.pieces.forEach(piece => {
            const [x, y] = piece.position;
            const cell = cells[y][x];
            piece.render(cell);
        });
    }
}
window.telepath.register('draughts.GameState', GameState)
```

Add a call to the `render` method in `games/templates/game.html`:

```html hl_lines="7"
        <script>
            document.addEventListener('DOMContentLoaded', event => {
                const gameElement = document.getElementById('game');
                const gameStateJson = gameElement.dataset.gameState;
                const packedGameState = JSON.parse(gameStateJson);
                const gameState = window.telepath.unpack(packedGameState);
                gameState.render(gameElement);
            })
        </script>
```

Reload the page, and you'll see our draughts board set up and ready for a game.

Let's take a quick look back at what we've achieved:

* We've packed and unpacked a data structure of custom Python / JavaScript types, without having to write code to recurse over that structure. If our GameState object becomes more complex (for example, the 'pieces' list might become a mixed list of Piece and King objects, or the state could include the game history) then there's no need to refactor any of the data packing / unpacking logic, other than providing an adapter object for each class used.
* Only the JS files necessary for unpacking the on-page data were served - if our gaming app expanded to cover Chess, Go and Othello, with all of the resulting classes registered with telepath, we'd still only need to serve the draughts-related code on this page.
* Even though we're working with arbitrary objects, no dynamic inline JavaScript was required - all dynamic data was passed as JSON, and all JavaScript code was fixed at deployment time (important if our site is enforcing [CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)).
