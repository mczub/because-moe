var express = require('express');
var app = express();

/*app.get('/', function(req, res){
	res.send('Hello World!');
});*/
app.set('view engine', 'jade');
app.get('/', function(req, res){
	res.render('index', {region: 'us'});
})
app.get('/us', function(req, res){
	res.render('index', {region: 'us'});
})
app.get('/ca', function(req, res){
	res.render('index', {region: 'ca'});
})
app.get('/uk', function(req, res){
	res.render('index', {region: 'uk'});
})
app.use('/', express.static('public', { maxAge: 86400000 }));

app.use(function(req, res, next) {
  res.status(404).send('File Not Found');
});
var port = process.env.PORT || 3000;
var server = app.listen(port, function () {
  var host = server.address().address;
  var port = server.address().port;

  console.log('Example app listening at http://%s:%s', host, port);
});