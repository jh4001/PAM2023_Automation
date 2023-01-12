const express = require("express");
const socket = require("socket.io");
const https = require('https');
const fs = require('fs');

// Certificate
const privateKey = fs.readFileSync('/path/to/licenses/privkey.pem', 'utf8');
const certificate = fs.readFileSync('/path/to/licenses/cert.pem', 'utf8');
const ca = fs.readFileSync('/path/to/licenses/chain.pem', 'utf8');

const credentials = {
    key: privateKey,
    cert: certificate,
    ca: ca
};

const app = express();

var httpsServer = https.createServer(credentials, app);

//Starts the server

let server = httpsServer.listen(4000, function () {
  console.log("Server is running");
});

app.use(express.static("public"));

//Upgrades the server to accept websockets.

let io = socket(server);

//Triggered when a client is connected.

io.on("connection", function (socket) {
  console.log("User Connected :" + socket.id);

  //Triggered when a peer hits the join room button.

  socket.on("join", function (roomName) {
    let rooms = io.sockets.adapter.rooms;
    let room = rooms.get(roomName);

    //room == undefined when no such room exists.
    if (room == undefined) {
      socket.join(roomName);
      socket.emit("created");
    } else if (room.size == 1) {
      //room.size == 1 when one person is inside the room.
      socket.join(roomName);
      socket.emit("joined");
    } else {
      //when there are already two people inside the room.
      socket.emit("full");
    }
    console.log(rooms);
  });

  //Triggered when the person who joined the room is ready to communicate.
  socket.on("ready", function (roomName) {
    socket.broadcast.to(roomName).emit("ready"); //Informs the other peer in the room.
  });

  //Triggered when server gets an icecandidate from a peer in the room.

  socket.on("candidate", function (candidate, roomName) {
    console.log(candidate);
    socket.broadcast.to(roomName).emit("candidate", candidate); //Sends Candidate to the other peer in the room.
  });

  //Triggered when server gets an offer from a peer in the room.

  socket.on("offer", function (offer, roomName) {
    socket.broadcast.to(roomName).emit("offer", offer); //Sends Offer to the other peer in the room.
  });

  //Triggered when server gets an answer from a peer in the room.

  socket.on("answer", function (answer, roomName) {
    socket.broadcast.to(roomName).emit("answer", answer); //Sends Answer to the other peer in the room.
  });
});
