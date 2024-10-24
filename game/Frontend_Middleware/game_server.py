import socket
import threading
import json
from game_logic import PokerGame

HOST = 'localhost'
PORT = 8080

class HTTPServer:
    def __init__(self):
        self.game = PokerGame()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        request = client_socket.recv(1024).decode('utf-8')
        method, path, _ = request.split('\n')[0].split()

        if method == 'POST' and path == '/start_game':
            self.game = PokerGame()
            response = self.create_response(200, json.dumps(self.game.get_public_game_state()))
        elif method == 'GET' and path == '/get_state':
            game_state = self.game.get_public_game_state()
            response = self.create_response(200, json.dumps(game_state))
        elif method == 'POST' and path == '/action':
            body = request.split('\r\n\r\n')[1]
            action_data = json.loads(body)
            result = self.game.process_action(action_data['action'], action_data.get('amount'))
            response = self.create_response(200, json.dumps(result))
        else:
            response = self.create_response(404, "Not Found")

        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()

    def create_response(self, status_code, body):
        status_messages = {200: 'OK', 404: 'Not Found'}
        headers = [
            f"HTTP/1.1 {status_code} {status_messages.get(status_code, '')}",
            "Content-Type: application/json",
            f"Content-Length: {len(body)}",
            "Connection: close"
        ]
        return '\r\n'.join(headers) + '\r\n\r\n' + body

if __name__ == '__main__':
    server = HTTPServer()
    server.start()