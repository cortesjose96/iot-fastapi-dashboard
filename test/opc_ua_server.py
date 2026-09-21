import asyncio
import logging
from asyncua import Server, ua

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("asyncua_server")

async def main():
    server = Server()
    await server.init()

    # Configuración de endpoint y nombre del servidor
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("AsyncUA Process Server")

    # Registro de Namespace personalizado
    namespace_uri = "http://industrial.iot/process/"
    idx = await server.register_namespace(namespace_uri)
    _logger.info(f"Namespace registrado '{namespace_uri}' con índice: {idx}")

    # Estructura del árbol de objetos
    objects_node = server.nodes.objects
    process_unit = await objects_node.add_object(idx, "ProcessUnit1")

    # Variables dentro del nodo:
    # 1. Variable de lectura/escritura (Setpoint de control)
    setpoint_node = await process_unit.add_variable(idx, "TemperatureSetpoint", 25.0)
    await setpoint_node.set_writable()  # Habilita escritura remota desde clientes

    # 2. Variable simulada (Temperatura del proceso)
    temperature_node = await process_unit.add_variable(idx, "ProcessTemperature", 20.0)
    await temperature_node.set_writable()

    _logger.info("Iniciando servidor OPC UA...")
    async with server:
        # Loop de ejecución del servidor
        simulated_temp = 20.0
        while True:
            await asyncio.sleep(2)
            # Lectura del setpoint actual escrito por un cliente
            current_sp = await setpoint_node.read_value()

            # Simulación de acercamiento al setpoint
            simulated_temp += (current_sp - simulated_temp) * 0.1
            await temperature_node.write_value(round(simulated_temp, 2))

            _logger.info(
                f"[Server Telemetría] Setpoint: {current_sp:.2f} °C | "
                f"Temp Actual: {simulated_temp:.2f} °C"
            )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")