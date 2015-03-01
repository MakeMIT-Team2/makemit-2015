var socket = io();
var s = 0;
var num = 0;
var data_from_server = []

setTimeout(function(){
	socket.on('d', function(d){
		data_from_server.push(d);
		console.log('Making cube!');
		console.log(d.x * (50/10) * 80, (7.8 - d.y) * (50/10) * 80, d.z * (50/10) * 80, d.str)
		makeCube((d.x * (50/10) * 60), (7.8 - d.y) * (50/10) * 60, d.z * (50/10) * 60 - 700, d.str);
	});
}, 1000);