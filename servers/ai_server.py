"""
Servidor de IA - THYONI TECH: Visual Security Guard
"""
import Pyro4
import os
import re
import time
import base64
from google import genai
from PIL import Image
import io

@Pyro4.expose
class AIServer(object):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("ERROR: GEMINI_API_KEY no configurada.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        self.analysis_count = 0
        print(f"[OK] Modelo Gemini activo: {self.model_name}")

    def analyze_image(self, frame_base64, analysis_type="security"):
        self.analysis_count += 1
        img_data = base64.b64decode(frame_base64)
        img = Image.open(io.BytesIO(img_data))

        prompts = {
            "security":    "Identifica lo que ves. Responde en 1 linea: '[Estado]: [Hallazgo]'.",
            "description": "Describe lo que ves en 1 linea.",
            "anomaly":     "Busca irregularidades. Responde: 'Anomalia: [Detalle]' o 'Sin anomalias'."
        }
        prompt = prompts.get(analysis_type, prompts["security"])
        
        for attempt in range(1, 4):
            try:
                response = self.client.models.generate_content(model=self.model_name, contents=[prompt, img])
                print(f"[OK] Análisis #{self.analysis_count} completado")
                return {
                    "status": "success",
                    "analysis_id": self.analysis_count,
                    "result": response.text
                }
            except Exception as e:
                if "429" in str(e) and attempt < 3:
                    time.sleep(5)
                else:
                    return {"status": "error", "message": str(e)}
        return {"status": "error", "message": "Reintentos agotados"}

    def get_status(self):
        return {"status": "online", "service": "edge.ai", "model": self.model_name}

    def get_analysis_count(self):
        return self.analysis_count

def main():
    host_ip = os.getenv("EDGE_SERVER_IP", "localhost")
    daemon = Pyro4.Daemon(host=host_ip, port=9092)
    
    try:
        ns = Pyro4.locateNS(host=host_ip, port=9090)
    except Exception:
        ns = Pyro4.locateNS(host="localhost", port=9090)
            
    server = AIServer()
    uri = daemon.register(server, "edge.ai")
    ns.register("edge.ai", uri)
    
    print(f"[OK] AI Server activo en {host_ip}:9092")
    daemon.requestLoop()

if __name__ == "__main__":
    main()