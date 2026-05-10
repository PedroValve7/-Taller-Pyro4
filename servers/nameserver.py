"""
Pyro4 Nameserver - THYONI TECH: Visual Security Guard
Registro centralizado de servicios distribuidos.
"""
import Pyro4.naming
import sys
import os

def start_nameserver():
    """Inicia el Pyro4 Nameserver usando la IP configurada."""
    # Lee la IP de la variable de entorno, por defecto localhost
    host_ip = os.getenv("EDGE_SERVER_IP", "localhost")
    port = 9090
    
    print(f"[OK] Iniciando Nameserver en {host_ip}:{port}...")
    try:
        Pyro4.naming.startNSloop(host=host_ip, port=port)
    except Exception as e:
        print(f"[X] Error al iniciar el Nameserver: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        start_nameserver()
    except KeyboardInterrupt:
        print("\nNameserver detenido.")