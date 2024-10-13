import asyncio

async def handle_client(reader, writer, target_server_address):
    # 创建到目标服务器的连接
    server_reader, server_writer = await asyncio.open_connection(*target_server_address)

    try:
        # 同时处理来自客户端和服务器的数据
        while True:
            # 等待数据从客户端接收
            data = await reader.read(4096)
            if not data:
                break
            # 数据发送到服务器
            server_writer.write(data)
            await server_writer.drain()

            # 等待数据从服务器接收
            response = await server_reader.read(4096)
            if not response:
                break
            # 数据发送回客户端
            writer.write(response)
            await writer.drain()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 关闭所有连接
        writer.close()
        server_writer.close()

async def run_server(server_address, server_port, server_targets):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, server_targets[next(server_index)]),
        server_address, server_port)
    async with server:
        await server.serve_forever()

server_address_list = [('rpyc-server1', 18812), ('rpyc-server2', 18812)]
server_index = iter(range(len(server_address_list)))

asyncio.run(run_server('0.0.0.0', 18888, server_address_list))
