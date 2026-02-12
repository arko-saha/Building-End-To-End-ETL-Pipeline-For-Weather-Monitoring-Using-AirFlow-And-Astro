from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from datetime import datetime, timedelta
import requests
import json

# Parameters for desired location (London, UK)
LATITUDE = '51.5074'
LONGITUDE = '-0.1278'
POSTGRES_CONN_ID = 'postgres_default'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG

with DAG(
    dag_id='weather_etl_pipeline', 
    default_args=default_args, 
    schedule='@daily', 
    catchup=False) as dags:
    
    @task()
    def extract_weather_data():
        # build the api endpoint
        url = f'https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'
        response = requests.get(url) 
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch weather data: {response.status_code}")
        
    @task()
    def transform_weather_data(weather_data):
        """Transform the extracted weather data."""
        current_weather = weather_data['current_weather']
        transformed_data = {
            'latitude': LATITUDE,
            'longitude': LONGITUDE,
            'temperature': current_weather['temperature'],
            'windspeed': current_weather['windspeed'],
            'winddirection': current_weather['winddirection'],
            'weathercode': current_weather['weathercode']
        }
        return transformed_data
    
    @task()
    def load_weather_data(transformed_data):
        """Load the transformed weather data into the database."""
        postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = postgres_hook.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS weather_data (
                           id SERIAL PRIMARY KEY,
                           latitude FLOAT,
                           longitude FLOAT,
                           temperature FLOAT,
                           windspeed FLOAT,
                           winddirection FLOAT,
                           weathercode INT,
                           timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       );
                       """)
        
        cursor.execute("""
                       INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       """, (transformed_data['latitude'], transformed_data['longitude'], transformed_data['temperature'], transformed_data['windspeed'], transformed_data['winddirection'], transformed_data['weathercode']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    # DAG workflow - ETL Pipeline
    
    weather_data = extract_weather_data()
    transformed_weather_data = transform_weather_data(weather_data)
    load_weather_data(transformed_weather_data)
    
    