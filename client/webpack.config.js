const path = require('path');

module.exports = {
  entry: {
    telepath: {
      import: ["./client/telepath.js"],
      filename: "telepath/static/telepath/telepath.js",
    }
  },
  output: {
    path: path.resolve('.'),
  }
}
