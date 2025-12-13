from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from datetime import datetime
from typing import Annotated, Optional
import asyncio
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# SQL - Tables
# ------------
class Sensor(SQLModel, table=True):
    id          : Optional[int] = Field(default=None, primary_key=True)
    name        : str = Field(index=True) #* "index=True" hace que las búsquedas por nombre sean rápidas
    location    : str
    model       : str

    reportes    : list["DeviceReport"] = Relationship(back_populates="sensor")

class DeviceReport(SQLModel, table=True):
    id          : Optional[int] = Field(default=None, primary_key=True)
    sensor_id   : int = Field(foreign_key="sensor.id") # Foreign Key
    temperature : float
    cpu         : int
    ram         : int
    disk        : int
    network     : int
    latency     : int
    timestamp   : datetime

    sensor      : Optional[Sensor] = Relationship(back_populates="reportes")

# SQL - Methods
# -------------
sqlite_file_name    = os.getenv("DB_NAME", "database.db")
sqlite_url          = f"sqlite:///{sqlite_file_name}"
engine              = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Users - Load
# ------------
load_dotenv()

usersDB = {
    os.getenv("ADMIN_USER"): {"password": os.getenv("ADMIN_PASSWORD"), "role": "admin"},
    os.getenv("GUEST_USER"): {"password": os.getenv("GUEST_PASSWORD"), "role": "guest"}
}

# Users - Verification
# --------------------
security = HTTPBasic()
async def verify_credentials(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    user = usersDB.get(credentials.username)

    await asyncio.sleep(0.5)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Credenciales incorrectas",
            headers     = {"WWW-Authenticate": "Basic"},
        )

    if user["password"] != credentials.password:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Credenciales incorrectas",
            headers     = {"WWW-Authenticate": "Basic"},
        )
    
    safe_user = {
        "username"  : credentials.username,
        "role"      : user["role"]
    }
    
    return safe_user

# FastAPI - life cycle
# --------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables() # Creamos la DB si no existe
    yield

app = FastAPI(lifespan=lifespan)

# FastAPI - Protection
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI - Endpoints
# -------------------
@app.post("/sensors")
async def create_sensor(sensor: Sensor, session: Session = Depends(get_session)):
    session.add(sensor)
    session.commit()
    session.refresh(sensor)
    return sensor

@app.post("/report")
async def receive_report(reporte: DeviceReport, session: Session = Depends(get_session)):
    if isinstance(reporte.timestamp, str):
        reporte.timestamp = datetime.fromisoformat(reporte.timestamp) # format "2025-12-07T..."
    session.add(reporte)
    session.commit()
    session.refresh(reporte)
    return reporte

@app.get("/sensors")
async def read_sensors(session: Session = Depends(get_session)):
    sensors = session.exec(select(Sensor)).all()
    return sensors

@app.get("/data")
async def data_show(
    user    : Annotated[dict, Depends(verify_credentials)],
    session : Session = Depends(get_session),
    limit   : int = 10
    ):
    statement   = select(DeviceReport).order_by(DeviceReport.id.desc()).limit(limit) # SQL: SELECT * FROM devicereport ORDER BY id DESC LIMIT 10
    results     = session.exec(statement).all()
    data        = list(reversed(results))

    if user['role'] == "admin":
        return data
    else:
        filteredReports = []
        for report in data:
            filteredReports.append({
                "temperature"   : report.temperature,
                "timestamp"     : report.timestamp
            })
        return filteredReports           

@app.get("/stats")
async def get_stats(session: Session = Depends(get_session)):
    statement   = select(DeviceReport)
    results     = session.exec(statement).all()

    if not results:
        return {"average_temperature": 0, "status": "no data"}
    
    total_temp  = sum(r.temperature for r in results)
    average     = total_temp / len(results)

    return {
        "average_temperature"   : round(average, 2),
        "total_reports"         : len(results)
    }