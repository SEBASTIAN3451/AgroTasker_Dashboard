# Imagen ligera de Python
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Copiar todo el dashboard
COPY . /app

# Variables por defecto (puedes sobreescribir en el proveedor)
ENV HOST=0.0.0.0
ENV PORT=8080

# Exponer el puerto
EXPOSE 8080

# Comando de inicio
CMD ["python", "server_simple.py"]
