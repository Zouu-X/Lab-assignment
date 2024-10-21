import asyncio
import itertools

async def health_check(server_targets, available_servers, update_iterator_event):
    while True:
        current_available = available_servers.copy()
        for server in list(server_targets):
            try:
                reader, writer = await asyncio.open_connection(*server)
                writer.close()
                await writer.wait_closed()
                if server not in current_available:
                    current_available.append(server)
                    print(f"Server {server} is now healthy.")
            except Exception as e:
                if server in current_available:
                    current_available.remove(server)
                    print(f"Server {server} is unhealthy, removing from targets. Error: {e}")
        if set(current_available) != set(available_servers):
            available_servers[:] = current_available
            update_iterator_event.set()
        await asyncio.sleep(10)

async def handle_client(reader, writer, available_servers, round_robin_iterator, update_iterator_event):
    while True:
        if update_iterator_event.is_set():
            round_robin_iterator = itertools.cycle(available_servers)
            update_iterator_event.clear()

        if not available_servers:
            print("No available servers to handle the request.")
            writer.close()
            await writer.wait_closed()
            return

        try:
            target_server_address = next(round_robin_iterator)
        except StopIteration:
            print("No available servers to forward the request.")
            writer.close()
            await writer.wait_closed()
            return

        try:
            server_reader, server_writer = await asyncio.open_connection(*target_server_address)
        except Exception as e:
            print(f"Failed to connect to target server {target_server_address}. Error: {e}")
            continue

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
            print(f"Error during data transfer: {e}")
        finally:
            writer.close()
            server_writer.close()
            return

async def run_server(server_address, server_port, server_targets):
    available_servers = server_targets.copy()
    round_robin_iterator = itertools.cycle(available_servers)
    update_iterator_event = asyncio.Event()

    asyncio.create_task(health_check(server_targets, available_servers, update_iterator_event))

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, available_servers, round_robin_iterator, update_iterator_event),
        server_address, server_port)
    async with server:
        await server.serve_forever()

server_address_list = [('rpyc-server1', 18812), ('rpyc-server2', 18812), ('rpyc-server3', 18812)]

asyncio.run(run_server('0.0.0.0', 18888, server_address_list))
