# Usa una imagen base con Python
FROM python:3.10.8-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que se ejecutará la aplicación Dash
EXPOSE 1250

# Comando para ejecutar la aplicación cuando se inicie el contenedor
CMD ["python", "app.py"]

