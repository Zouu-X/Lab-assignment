import socket
import select

def handle_client(client_socket, target_server_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.connect(target_server_address)

        # 将客户端socket和服务器socket加入到同一个循环中，进行数据转发
        sockets_list = [client_socket, server_socket]
        running = True

        while running:
            # 可读socket列表
            readable, _, _ = select.select(sockets_list, [], sockets_list, 0.5)

            if not readable:
                continue

            for sock in readable:
                try:
                    data = sock.recv(4096)  # 尝试从socket读取数据
                    if data:
                        # 数据来自客户端，发送到服务器；来自服务器，发送回客户端
                        if sock is client_socket:
                            server_socket.sendall(data)
                        else:
                            client_socket.sendall(data)
                    else:
                        # 没有数据表示连接已关闭
                        running = False
                        break
                except Exception as e:
                    print(f"Error: {e}")
                    running = False
                    break

def main():
    server_address_list = [('rpyc-server1', 18812), ('rpyc-server2', 18812)]
    current_server = 0

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 18888))
    server.listen(5)

    try:
        while True:
            client_socket, client_address = server.accept()
            print(f"Accepted connection from {client_address}")

            target_server_address = server_address_list[current_server]
            current_server = (current_server + 1) % len(server_address_list)

            # 处理客户端请求
            handle_client(client_socket, target_server_address)
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main()
