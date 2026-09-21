import asyncio
import logging
from asyncua import Client, ua

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("asyncua_client")

async def main():
    url = "opc.tcp://127.0.0.1:4840/freeopcua/server/"
    namespace_uri = "http://industrial.iot/process/"

    async with Client(url=url) as client:
        _logger.info("Conectado exitosamente al servidor OPC UA.")

        # Obtener el índice del Namespace dinámicamente a través del URI
        try:
            idx = await client.get_namespace_index(namespace_uri)
            _logger.info(f"Índice resuelto para '{namespace_uri}': {idx}")
        except Exception as e:
            _logger.error(f"El Namespace '{namespace_uri}' no existe en el servidor: {e}")
            return

        # Localizar nodos por ruta relativa desde el nodo Objects
        objects_node = client.nodes.objects
        setpoint_node = await objects_node.get_child([f"{idx}:ProcessUnit1", f"{idx}:TemperatureSetpoint"])
        temp_node = await objects_node.get_child([f"{idx}:ProcessUnit1", f"{idx}:ProcessTemperature"])

        # 1. Leer valores actuales
        current_sp = await setpoint_node.read_value()
        current_temp = await temp_node.read_value()
        _logger.info(f"[Lectura inicial] Setpoint: {current_sp} | Temp: {current_temp}")

        # 2. Escribir un nuevo valor en el Setpoint
        new_setpoint = 42.5
        _logger.info(f"Escribiendo nuevo Setpoint: {new_setpoint}...")

        # Forma explícita con tipo de dato Variant (recomendada para evitar ambigüedades)
        datavalue = ua.DataValue(ua.Variant(new_setpoint, ua.VariantType.Double))
        await setpoint_node.write_value(datavalue)

        # 3. Confirmar la escritura
        await asyncio.sleep(0.5)
        verified_sp = await setpoint_node.read_value()
        _logger.info(f"[Verificación] Setpoint confirmado en servidor: {verified_sp}")

if __name__ == "__main__":
    asyncio.run(main())