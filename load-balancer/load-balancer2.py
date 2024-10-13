# 使用Least Connection
import asyncio
import collections

servers = {
    'rpyc-server1:18812': 0,
    'rpyc-server2:18812': 0,
    'rpyc-server3:18812': 0,
}

#获取最少连接服务器
def get_least_connection_server():
    return min(servers, key=servers.get)

async def handle_client(reader, writer):
    server_address = get_least_connection_server()
    server_host, server_port = server_address.split(':')
    server_port = int(server_port)

    # 增加选定服务器连接数
    servers[server_address] += 1

    server_reader, server_writer = await asyncio.open_connection(server_host, server_port)
    try:
        await asyncio.gather(
            relay(reader, server_writer),
            relay(server_reader, writer),
        )
    finally:
        # 减少选定服务器连接数
        servers[server_address] -= 1
        writer.close()
        server_writer.close()

async def relay(source, dest):
    while True:
        data = await source.read(4096)
        if not data:
            break
        dest.write(data)
        await dest.drain()

async def run_server(host, port):
    server = await asyncio.start_server(
        handle_client, host, port
    )
    async with server:
        await server.serve_forever()

asyncio.run(run_server('0.0.0.0', 18888))