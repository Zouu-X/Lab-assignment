import asyncio
import itertools

async def health_check(server_targets, available_servers):
    while True:
        for server in list(server_targets):  # Create a copy to allow modification
            try:
                reader, writer = await asyncio.open_connection(*server)
                writer.close()
                await writer.wait_closed()
                if server not in available_servers:
                    available_servers.append(server)  # Add server back if it is healthy
            except Exception as e:
                if server in available_servers:
                    print(f"Server {server} is unhealthy, removing from targets. Error: {e}")
                    available_servers.remove(server)
        await asyncio.sleep(10)  # Perform health check every 10 seconds

async def handle_client(reader, writer, available_servers):
    if not available_servers:
        print("No available servers to handle the request.")
        writer.close()
        await writer.wait_closed()
        return

    target_server_address = next(itertools.cycle(available_servers))
    try:
        server_reader, server_writer = await asyncio.open_connection(*target_server_address)
    except Exception as e:
        print(f"Failed to connect to target server {target_server_address}. Error: {e}")
        writer.close()
        await writer.wait_closed()
        return

    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            server_writer.write(data)
            await server_writer.drain()

            response = await server_reader.read(4096)
            if not response:
                break
            writer.write(response)
            await writer.drain()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        writer.close()
        server_writer.close()

async def run_server(server_address, server_port, server_targets):
    available_servers = server_targets.copy()  # Keep track of currently available servers

    # Run health check task in the background
    asyncio.create_task(health_check(server_targets, available_servers))

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, available_servers),
        server_address, server_port)
    async with server:
        await server.serve_forever()

server_address_list = [('rpyc-server1', 18812), ('rpyc-server2', 18812), ('rpyc-server3', 18812)]

asyncio.run(run_server('0.0.0.0', 18888, server_address_list))
