<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Dashboard</title>
  <link rel="stylesheet" href="static/css/materialize.min.css">
</head>
<body>
  <div class="row">
    <div class="col s12 m6">
      <table class="responsive-table">
        <thead>
          <tr>
              <th>Key</th>
              <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>foo</td>
            <td id="foo">{{ data.get('foo') if data else "no data" }}</td>
          </tr>
          <tr>
            <td>baz</td>
            <td id="baz">{{ data.get('baz') if data else "no data" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <script src="static/js/materialize.min.js"></script>
  <script type="text/javascript">
    let foo = document.getElementById("foo");
    let baz = document.getElementById("baz");
    let ws = new WebSocket("wss://"+window.location.host+"/websocket");
    //ws.onopen = function() {
    //    ws.send(Math.random());
    //};
    ws.onmessage = function (evt) {
      data = JSON.parse(evt.data);
      foo.innerText = data.foo;
      baz.innerText = data.baz;
    };
  </script>
</body>
</html>