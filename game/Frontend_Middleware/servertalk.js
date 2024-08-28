let port = 8765
let uri = "localhost"

// Create WebSocket connection.
const websock = new WebSocket("ws://"+uri+":"+port);

// Listen for messages
websock.addEventListener("message", (event) => {
  console.log("Message from server ", event.data);
});
