var express = require('express');
var app = express();

/*app.get('/', function(req, res){
	res.send('Hello World!');
});*/

app.use(express.static('public'));

app.use(function(req, res, next) {
  res.status(404).send('File Not Found');
});
var port = process.env.PORT || 3000;
var server = app.listen(port, function () {
  var host = server.address().address;
  var port = server.address().port;

  console.log('Example app listening at http://%s:%s', host, port);
});