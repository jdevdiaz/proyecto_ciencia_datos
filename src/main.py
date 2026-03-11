import pandas as pd
import requests

def run_etl():
    # 1. Extracción de datos (Socrata - Datos Abiertos Colombia)
    url = "https://www.datos.gov.co/resource/ji8i-4anb.json?$limit=10000"
    print("Iniciando descarga de datos...")
    
    try:
        response = requests.get(url)
        df = pd.DataFrame(response.json())
        
        # 2. LIMPIEZA AGRESIVA (El secreto para que el dashboard no falle)
        # Convertimos todo a minúsculas y quitamos tildes/espacios
        df.columns = (df.columns.str.lower()
                      .str.replace('ó', 'o').str.replace('á', 'a')
                      .str.replace('í', 'i').str.replace('é', 'e')
                      .str.strip())

        # 3. CORRECCIÓN DE COLUMNAS (Mapeo manual para evitar errores)
        mapping = {
            'tamano_promedio_de_grupo': 'tamano_promedio_grupo', 
            'año': 'ano',
            'c_digo_departamento': 'codigo_depto'
        }
        df = df.rename(columns=mapping)

        # 4. CONVERSIÓN NUMÉRICA
        # Columnas que deben ser números para poder graficar
        cols_num = ['poblacion_5_16', 'cobertura_neta', 'cobertura_bruta', 
                    'desercion', 'aprobacion', 'reprobacion', 'repitencia', 
                    'tamano_promedio_grupo']
        
        for col in cols_num:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                # Si el dato es > 1 (ej. 95%), lo pasamos a escala 0-1 (0.95)
                if col not in ['poblacion_5_16', 'tamano_promedio_grupo']:
                    df[col] = df[col].apply(lambda x: x/100 if x > 2 else x)

        # 5. Guardar el archivo final
        df.to_csv("data/processed/datos_educacion_limpios.csv", index=False)
        print("✅ Archivo 'datos_educacion_limpios.csv' generado con éxito.")

    except Exception as e:
        print(f"❌ Error en el proceso: {e}")

if __name__ == "__main__":
    run_etl()