Programa amigable para el usuario con interfaz grafica usado para normalizar el audio de videos.

## Usos

- Aumentar el volumen general de todo el video.
- Equilibrar la intensidad de los sonidos fuertes.

## Requisitos
1. Python 3.12.8
2. Este programa ejecuta de fondo `ffmpeg` para funcionar. Puede <a href="https://ffmpeg.org/download.html" target="_blank">instalarlo</a> mediante su gestor de paquetes de preferencia o sus compilaciones oficiales.
  
## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/martinmsq/ref_sound_mov.git
cd ref_sound_mov
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar:
```bash
python interface.py
```

## Configuración

Para la configuración se hace uso de sus tres filtros o parámetros:
- Nivel Sonoro Promedio:
- Rango Sonoro:
- Picos Sonoros:

## Uso

1. Seleccionar el archivo de video.
2. Seleccionar alguna opcion predeterminada(TV/Living, Auriculares, Home Cinema) o ajustar los parámetros manualmente.
3. Ejecutar "Iniciar".
