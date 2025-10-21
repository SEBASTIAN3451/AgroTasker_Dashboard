from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import os

# Cambiar al directorio donde está el archivo HTML
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configurar el servidor
PORT = 8000
Handler = SimpleHTTPRequestHandler
httpd = HTTPServer(("", PORT), Handler)

print(f"Servidor iniciado en http://localhost:{PORT}")
print("Abriendo el navegador automáticamente...")

# Abrir el navegador automáticamente
webbrowser.open(f"http://localhost:{PORT}")

# Mantener el servidor funcionando
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServidor detenido.")
    httpd.server_close()