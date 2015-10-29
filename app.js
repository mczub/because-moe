var express = require('express');
var request = require('request');
var app = express();

/*app.get('/', function(req, res){
	res.send('Hello World!');
});*/
app.set('view engine', 'jade');
app.get('/', function(req, res){
	res.render('index', {region: 'us', query: (req.query.q) ? req.query.q : ""});
})
app.get('/us', function(req, res){
	res.render('index', {region: 'us', query: (req.query.q) ? req.query.q : ""});
})
app.get('/ca', function(req, res){
	res.render('index', {region: 'ca', query: (req.query.q) ? req.query.q : ""});
})
app.get('/uk', function(req, res){
	res.render('index', {region: 'uk', query: (req.query.q) ? req.query.q : ""});
})
app.get('/au', function(req, res){
	res.render('index', {region: 'au', query: (req.query.q) ? req.query.q : ""});
})
app.get('/json/:country', function(req,res){
	var jsonUrl = "https://bcmoe.blob.core.windows.net/assets/" + req.params.country + ".json";
	//res.setHeader('Cache-Control', 'public, max-age=432000');
	request(jsonUrl).pipe(res)
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