# ETL Weather Pipeline 🌦️

> [!TIP]
> **TL;DR**: A fully automated Airflow pipeline that fetches real-time London weather data from Open-Meteo, saves it to a PostgreSQL database (`postgres-db`), and allows live monitoring via dBeaver. Runs entirely in Docker via Astronomer.

A robust, containerized ETL pipeline that fetches real-time weather data for London and persists it into a PostgreSQL database for analysis. Built with Apache Airflow and Astronomer.

---

## 🚀 Overview

This project demonstrates a production-grade MLOps foundational layer: reliable data ingestion. It automates the extraction of weather metrics (temperature, windspeed, etc.) from the Open-Meteo API, transforms the raw JSON into a structured format, and loads it into a custom PostgreSQL instance named `postgres-db`.

---

## 🛠️ Technical Stack

- **Orchestration**: [Apache Airflow](https://airflow.apache.org/) (TaskFlow API)
- **Environment**: [Astronomer CLI (Astro)](https://www.astronomer.io/docs/astro/cli/get-started)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **Database**: [PostgreSQL 12](https://www.postgresql.org/)
- **Data Source**: [Open-Meteo API](https://open-meteo.com/) (Free, no API key required)
- **Monitoring**: [dBeaver](https://dbeaver.io/) (for live SQL data visualization)

---

## 🏗️ Architecture

The pipeline follows a classic **Extract-Transform-Load (ETL)** pattern:

1. **Extract**: Airflow triggers a Python task that calls the Open-Meteo API using the `requests` library to fetch current weather data for specific coordinates (London: 51.5°N, -0.1°W).
2. **Transform**: The raw JSON response is parsed to extract key metrics:
    - Temperature (°C)
    - Windspeed (km/h)
    - Wind Direction (degrees)
    - Weather Code (WMO standard)
3. **Load**: The structured data is pushed to a dedicated table (`weather_data`) in the PostgreSQL database using the `PostgresHook`.

```mermaid
graph LR
    API[Open-Meteo API] -->|JSON| Airflow[Apache Airflow]
    Airflow -->|ETL Logic| DB[(PostgreSQL: postgres-db)]
    DB <-->|Live SQL Query| dBeaver[dBeaver Visualization]
```

---

## 🔧 Setup & Deployment

### 1. Prerequisites

- Docker Desktop installed and running.
- [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) installed.

### 2. Launch the Environment

Navigate to the project root and run:

```bash
astro dev start
```

This will spin up:

- **Webserver**: Airflow UI at `http://localhost:8080` (admin/admin)
- **Postgres**: Named `postgres-db` (mapped to localhost:5432)
- **Scheduler/Triggerer**: Monitoring and executing your DAGs.

### 3. Verify the Container

The database container is specially configured for easy access:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
# Look for 'postgres-db'
```

---

## 📊 Live Monitoring with dBeaver

We used **dBeaver** to monitor the data ingestion in real-time. Here is how to connect:

1. **Host**: `localhost`
2. **Port**: `5432`
3. **Database**: `postgres`
4. **Username**: `postgres`
5. **Password**: `postgres`

**Live SQL Query:**

```sql
SELECT * FROM weather_data ORDER BY timestamp DESC;
```

---

## ⚡ Useful Commands

- **Trigger the DAG**: Go to the Airflow UI (localhost:8080) and toggle the `weather_etl_pipeline` on.
- **Check Logs (CLI)**: `astro dev logs --scheduler`
- **Restart Services**: `astro dev restart`
- **Direct DB Check**:

```bash
docker exec -it postgres-db psql -U postgres -c "SELECT * FROM weather_data;"
```
