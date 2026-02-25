---
name: webrtc-communication
description: WebRTC real-time communication covering peer connections, media streams, data channels, STUN/TURN servers, signaling with WebSocket, screen sharing, and integration with React and Node.js.
---

# WebRTC Communication

This skill should be used when implementing real-time communication with WebRTC. It covers peer connections, media streams, data channels, signaling, and screen sharing.

## When to Use This Skill

Use this skill when you need to:

- Build video/audio calling features
- Implement peer-to-peer data channels
- Set up signaling servers with WebSocket
- Handle screen sharing and media recording
- Configure STUN/TURN servers for NAT traversal

## Basic Peer Connection

```typescript
// Create peer connection with STUN/TURN
const config: RTCConfiguration = {
  iceServers: [
    { urls: "stun:stun.l.google.com:19302" },
    {
      urls: "turn:turn.example.com:3478",
      username: "user",
      credential: "pass",
    },
  ],
};

const pc = new RTCPeerConnection(config);

// Handle ICE candidates
pc.onicecandidate = (event) => {
  if (event.candidate) {
    signalingServer.send(JSON.stringify({
      type: "ice-candidate",
      candidate: event.candidate,
    }));
  }
};

// Handle remote stream
pc.ontrack = (event) => {
  const remoteVideo = document.getElementById("remote") as HTMLVideoElement;
  remoteVideo.srcObject = event.streams[0];
};
```

## Signaling Server (Node.js)

```typescript
import { WebSocketServer, WebSocket } from "ws";

const wss = new WebSocketServer({ port: 8080 });
const rooms = new Map<string, Set<WebSocket>>();

wss.on("connection", (ws) => {
  let currentRoom: string | null = null;

  ws.on("message", (data) => {
    const message = JSON.parse(data.toString());

    switch (message.type) {
      case "join": {
        currentRoom = message.room;
        if (!rooms.has(currentRoom!)) rooms.set(currentRoom!, new Set());
        rooms.get(currentRoom!)!.add(ws);
        break;
      }
      case "offer":
      case "answer":
      case "ice-candidate": {
        // Relay to other peers in room
        if (currentRoom && rooms.has(currentRoom)) {
          rooms.get(currentRoom)!.forEach((peer) => {
            if (peer !== ws && peer.readyState === WebSocket.OPEN) {
              peer.send(JSON.stringify(message));
            }
          });
        }
        break;
      }
    }
  });

  ws.on("close", () => {
    if (currentRoom && rooms.has(currentRoom)) {
      rooms.get(currentRoom)!.delete(ws);
      if (rooms.get(currentRoom)!.size === 0) rooms.delete(currentRoom);
    }
  });
});
```

## Offer/Answer Exchange

```typescript
// Caller — create offer
async function createOffer(pc: RTCPeerConnection, ws: WebSocket) {
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  ws.send(JSON.stringify({ type: "offer", sdp: offer }));
}

// Callee — handle offer and create answer
async function handleOffer(
  pc: RTCPeerConnection,
  offer: RTCSessionDescriptionInit,
  ws: WebSocket,
) {
  await pc.setRemoteDescription(new RTCSessionDescription(offer));
  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);
  ws.send(JSON.stringify({ type: "answer", sdp: answer }));
}

// Caller — handle answer
async function handleAnswer(
  pc: RTCPeerConnection,
  answer: RTCSessionDescriptionInit,
) {
  await pc.setRemoteDescription(new RTCSessionDescription(answer));
}

// Both — handle ICE candidate
async function handleIceCandidate(
  pc: RTCPeerConnection,
  candidate: RTCIceCandidateInit,
) {
  await pc.addIceCandidate(new RTCIceCandidate(candidate));
}
```

## Media Streams

```typescript
// Get user media
async function getLocalStream() {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { width: 1280, height: 720, facingMode: "user" },
    audio: { echoCancellation: true, noiseSuppression: true },
  });

  // Add tracks to peer connection
  stream.getTracks().forEach((track) => pc.addTrack(track, stream));
  return stream;
}

// Toggle audio/video
function toggleAudio(stream: MediaStream) {
  stream.getAudioTracks().forEach((track) => {
    track.enabled = !track.enabled;
  });
}

function toggleVideo(stream: MediaStream) {
  stream.getVideoTracks().forEach((track) => {
    track.enabled = !track.enabled;
  });
}

// Screen sharing
async function startScreenShare() {
  const screenStream = await navigator.mediaDevices.getDisplayMedia({
    video: { cursor: "always" },
    audio: false,
  });

  const videoTrack = screenStream.getVideoTracks()[0];
  const sender = pc.getSenders().find((s) => s.track?.kind === "video");
  sender?.replaceTrack(videoTrack);

  videoTrack.onended = () => {
    // Revert to camera
    const cameraTrack = localStream.getVideoTracks()[0];
    sender?.replaceTrack(cameraTrack);
  };
}
```

## Data Channels

```typescript
// Create data channel (caller side)
const dataChannel = pc.createDataChannel("chat", {
  ordered: true,
});

dataChannel.onopen = () => console.log("Data channel open");
dataChannel.onmessage = (event) => {
  const message = JSON.parse(event.data);
  displayMessage(message);
};

// Send message
dataChannel.send(JSON.stringify({ text: "Hello!", timestamp: Date.now() }));

// Receive data channel (callee side)
pc.ondatachannel = (event) => {
  const channel = event.channel;
  channel.onmessage = (event) => {
    const message = JSON.parse(event.data);
    displayMessage(message);
  };
};
```

## React Hook

```tsx
import { useRef, useState, useCallback, useEffect } from "react";

function useWebRTC(signalingUrl: string, roomId: string) {
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);

  const init = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true, audio: true,
    });
    setLocalStream(stream);

    const pc = new RTCPeerConnection(config);
    pcRef.current = pc;

    stream.getTracks().forEach((track) => pc.addTrack(track, stream));

    pc.ontrack = (event) => setRemoteStream(event.streams[0]);

    const ws = new WebSocket(signalingUrl);
    wsRef.current = ws;

    ws.onopen = () => ws.send(JSON.stringify({ type: "join", room: roomId }));

    ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "offer") await handleOffer(pc, msg.sdp, ws);
      if (msg.type === "answer") await handleAnswer(pc, msg.sdp);
      if (msg.type === "ice-candidate") await handleIceCandidate(pc, msg.candidate);
    };

    pc.onicecandidate = (e) => {
      if (e.candidate) {
        ws.send(JSON.stringify({ type: "ice-candidate", candidate: e.candidate }));
      }
    };
  }, [signalingUrl, roomId]);

  const cleanup = useCallback(() => {
    localStream?.getTracks().forEach((t) => t.stop());
    pcRef.current?.close();
    wsRef.current?.close();
  }, [localStream]);

  useEffect(() => () => cleanup(), [cleanup]);

  return { localStream, remoteStream, init, cleanup, pc: pcRef };
}
```

## Additional Resources

- WebRTC API: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
- WebRTC samples: https://webrtc.github.io/samples/
