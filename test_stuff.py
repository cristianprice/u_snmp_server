import socket


def udp_server(host='0.0.0.0', port=12345):
    # Create a new socket using the given network family and socket type
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ai = socket.getaddrinfo(host, port)
    print(ai)
    s.bind(ai[0][-1])

    print('UDP Server listening on {}:{}'.format(host, port))

    while True:
        # Receive data from the socket, up to a maximum of 1024 bytes
        data, addr = s.recvfrom(1024)
        print('Received message:', data, 'from:', addr)


# Start the server
udp_server()
