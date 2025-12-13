# IoT Monitoring System - Backend & Dashboard

Sistema de monitoreo industrial desarrollado con **Python (FastAPI)** y **SQLite**. Simula la ingesta de datos de sensores IoT en tiempo real y visualiza métricas clave.

## Tecnologías
* **Backend:** FastAPI, Uvicorn, SQLModel (ORM).
* **Base de Datos:** SQLite (Relacional).
* **Frontend/Viz:** Streamlit, Plotly.
* **Seguridad:** Variables de entorno (.env), CORS middleware.

## Instalación
1. Clonar el repositorio:
```bash
   git clone [https://github.com/TU_USUARIO/iot-fastapi-dashboard.git](https://github.com/TU_USUARIO/iot-fastapi-dashboard.git)
```

2. Crear entorno virtual e instalar dependencias:
```bash
    pip install -r requirements.txt
```

3. Configurar variables de entorno: Crear un archivo .env basado en los requisitos (DB_NAME, ADMIN_USER, etc).

4. **Ejecución:**
   Abre 3 terminales diferentes y ejecuta los siguientes comandos en orden:

   * **Backend:** (Terminal 1)
     ```bash
     uvicorn main:app --reload
     ```

   * **Simulador:** (Terminal 2)
     ```bash
     python sim_sensor.py
     ```

   * **Dashboard:** (Terminal 3)
     ```bash
     streamlit run live_dashboard.py
     ```