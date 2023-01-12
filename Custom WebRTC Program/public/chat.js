let socket = io.connect("https://your.domain:4000");
let divVideoChatLobby = document.getElementById("video-chat-lobby");
let divVideoChat = document.getElementById("video-chat-room");
let joinButton = document.getElementById("join");
let userVideo = document.getElementById("user-video");
let peerVideo = document.getElementById("peer-video");
let roomInput = document.getElementById("roomName");
let roomName;
let creator = false;
let rtcPeerConnection;
let userStream;

var stats_dict = {};

// Contains the stun server URL we will be using.
let iceServers = {
  iceServers: [
    { urls: "stun:stun.services.mozilla.com" },
    { urls: "stun:stun.l.google.com:19302" },
  ],
};

joinButton.addEventListener("click", function () {
  if (roomInput.value == "") {
    alert("Please enter a room name");
  } else {
    roomName = roomInput.value;
    socket.emit("join", roomName);
  }
});

// Triggered when a room is succesfully created.

socket.on("created", function () {
  creator = true;

  navigator.mediaDevices
    .getUserMedia({
      audio: true,
      video: { width: 1280, height: 720 },
    })
    .then(function (stream) {
      /* use the stream */
      userStream = stream;
      divVideoChatLobby.style = "display:none";
      userVideo.srcObject = stream;
      userVideo.onloadedmetadata = function (e) {
        userVideo.play();
      };
    })
    .catch(function (err) {
      /* handle the error */
      alert("Couldn't Access User Media");
    });
});

// Triggered when a room is succesfully joined.

socket.on("joined", function () {
  creator = false;

  navigator.mediaDevices
    .getUserMedia({
      audio: true,
      video: { width: 1280, height: 720 },
    })
    .then(function (stream) {
      /* use the stream */
      userStream = stream;
      divVideoChatLobby.style = "display:none";
      userVideo.srcObject = stream;
      userVideo.onloadedmetadata = function (e) {
        userVideo.play();
      };
      socket.emit("ready", roomName);
    })
    .catch(function (err) {
      /* handle the error */
      alert("Couldn't Access User Media");
    });
});

// Triggered when a room is full (meaning has 2 people).

socket.on("full", function () {
  alert("Room is Full, Can't Join");
});

// Triggered when a peer has joined the room and ready to communicate.

socket.on("ready", function () {
  if (creator) {
    rtcPeerConnection = new RTCPeerConnection(iceServers);
    rtcPeerConnection.onicecandidate = OnIceCandidateFunction;
    rtcPeerConnection.ontrack = OnTrackFunction;
    rtcPeerConnection.addTrack(userStream.getTracks()[0], userStream);
    rtcPeerConnection.addTrack(userStream.getTracks()[1], userStream);

    // https://stackoverflow.com/a/70843114
    // let tcvr = rtcPeerConnection.getTransceivers()[1];
    // let codecs = RTCRtpReceiver.getCapabilities('video').codecs;
    // let new_codecs = [];
    // // iterate over supported codecs and pull out the codecs we want
    // for(let i = 0; i < codecs.length; i++)
    // {
    //    if(codecs[i].mimeType == "video/VP9")
    //    {
    //       new_codecs.push(codecs[i]);
    //    }
    // }
    // // currently not all browsers support setCodecPreferences
    // if(tcvr.setCodecPreferences != undefined)
    // {
    //    tcvr.setCodecPreferences(new_codecs);
    // }

    rtcPeerConnection
      .createOffer()
      .then((offer) => {
        rtcPeerConnection.setLocalDescription(offer);
        socket.emit("offer", offer, roomName);
      })

      .catch((error) => {
        console.log(error);
      });
    setTimeout(() => { 
        buildWebRTCStatsDict();
        statsInterval = window.setInterval(getVideoStats, 1000);
      }, 2000);
  }
});

// Triggered on receiving an ice candidate from the peer.

socket.on("candidate", function (candidate) {
  let icecandidate = new RTCIceCandidate(candidate);
  rtcPeerConnection.addIceCandidate(icecandidate);
});

// Triggered on receiving an offer from the person who created the room.

socket.on("offer", function (offer) {
  if (!creator) {
    rtcPeerConnection = new RTCPeerConnection(iceServers);
    rtcPeerConnection.onicecandidate = OnIceCandidateFunction;
    rtcPeerConnection.ontrack = OnTrackFunction;
    rtcPeerConnection.addTrack(userStream.getTracks()[0], userStream);
    rtcPeerConnection.addTrack(userStream.getTracks()[1], userStream);

    // https://stackoverflow.com/a/70843114
    // let tcvr = rtcPeerConnection.getTransceivers()[1];
    // let codecs = RTCRtpReceiver.getCapabilities('video').codecs;
    // let new_codecs = [];
    // // iterate over supported codecs and pull out the codecs we want
    // for(let i = 0; i < codecs.length; i++)
    // {
    //    if(codecs[i].mimeType == "video/VP9")
    //    {
    //       new_codecs.push(codecs[i]);
    //    }
    // }
    // // currently not all browsers support setCodecPreferences
    // if(tcvr.setCodecPreferences != undefined)
    // {
    //    tcvr.setCodecPreferences(new_codecs);
    // }

    rtcPeerConnection.setRemoteDescription(offer);
    rtcPeerConnection
      .createAnswer()
      .then((answer) => {
        rtcPeerConnection.setLocalDescription(answer);
        socket.emit("answer", answer, roomName);
      })
      .catch((error) => {
        console.log(error);
      });
    setTimeout(() => { 
        buildWebRTCStatsDict();
        statsInterval = window.setInterval(getVideoStats, 1000);
      }, 2000);
  }
});

// Triggered on receiving an answer from the person who joined the room.

socket.on("answer", function (answer) {
  rtcPeerConnection.setRemoteDescription(answer);
});

// Implementing the OnIceCandidateFunction which is part of the RTCPeerConnection Interface.

function OnIceCandidateFunction(event) {
  console.log("Candidate");
  if (event.candidate) {
    socket.emit("candidate", event.candidate, roomName);
  }
}

// Implementing the OnTrackFunction which is part of the RTCPeerConnection Interface.

function OnTrackFunction(event) {
  peerVideo.srcObject = event.streams[0];
  peerVideo.onloadedmetadata = function (e) {
    peerVideo.play();
  };
}

/*
  Goal is to build a stats dictionary which has this structure:
  {
    Report-ID_1 = {
                    stat1 = [...]
                    stat2 = [...]
                    stat3 = [...]
                    ...
                  }
    Report-ID_2 = {
                    stat1 = [...]
                    stat2 = [...]
                    stat3 = [...]
                  }
    ...
  }
*/
function buildWebRTCStatsDict() {
  rtcPeerConnection.getStats(null).then(stats => {
    stats.forEach(report => {
      if (report.type === "inbound-rtp" && report.mediaType === "video") {
        stats_dict[report.id] = {};
        Object.keys(report).forEach(statName => {
          stats_dict[report.id][statName] = [];
        });
      }
      else if (report.type === "outbound-rtp" && report.mediaType === "video") {
        stats_dict[report.id] = {};
        Object.keys(report).forEach(statName => {
          stats_dict[report.id][statName] = [];
        });
      }
    });
  });
}

function getVideoStats() {
  rtcPeerConnection.getStats(null).then(stats => {
    stats.forEach(report => {
      if (report.type === "inbound-rtp" && report.mediaType === "video") {
        Object.keys(report).forEach(statName => {
          try {
            stats_dict[report.id][statName].push(report[statName]);
          }
          catch {
            console.log(statName)
          }
        });
      }
      else if (report.type === "outbound-rtp" && report.mediaType === "video") {
        Object.keys(report).forEach(statName => {
          try {
            stats_dict[report.id][statName].push(report[statName]);
          }
          catch {
            console.log(statName)
          }
        });
      }
    });
  });
  console.log(stats_dict);
}

/*
  There is no real way to download a file in Javascript
  We basically have to format our JSON file into a URI, 
  which can then be used as a temporary link on the webpage
  When the link is clicked, the file will be downloaded.
  Then we can remove the link 

  https://stackoverflow.com/a/18197341
*/
function downloadVideoStats() {
  // build the JSON dictionary
  let stats_data = JSON.stringify(stats_dict, null, 2);
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(stats_data));
  element.setAttribute('download', "webrtc_video_stats.txt");

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function stopVideo() {
  userStream.getTracks().forEach(function(track) {
        if (track.readyState == 'live' && track.kind === 'video') {
            track.enabled = false;
        }
    });
}

function startVideo() {
  userStream.getTracks().forEach(function(track) {
        if (track.readyState == 'live' && track.kind === 'video') {
            track.enabled = true;
        }
    });
}

function stopAudio() {
  userStream.getTracks().forEach(function(track) {
        if (track.readyState == 'live' && track.kind === 'audio') {
            track.enabled = false;
        }
    });
}
