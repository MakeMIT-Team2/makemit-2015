var express = require('express');
var sockCount = 0;
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io')(server);
var port = 8080;
var hist = [0, 0];

server.listen(port, function () {
	console.log('Server listening at port %d', port);
});
app.get('/poll', function(req, res){
	var strength = (parseFloat(req.query.d))/70;
	if (Date.now() - hist[1] < 1000 * 1) { // 1 sec
		var d = {
			str:strength,
			x:hist[0].x,
			y:hist[0].y,
			z:hist[0].z
		};

		io.emit('d', d);
	}
	console.log(strength)
	res.status(200).end();
});

app.use(express.static(__dirname + '/static'));
io.on('connection', function(socket) {
	console.log("socket connected!")
	socket.on('pos', function(d) {
		hist = ([d, Date.now()]);
	})
});

io.on('connect', function() { sockCount++; });
io.on('disconnect', function() { sockCount--; });
