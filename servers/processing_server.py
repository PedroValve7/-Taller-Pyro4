"""
Servidor de Procesamiento Local - THYONI TECH: Visual Security Guard
"""
import Pyro4
import cv2
import numpy as np
import base64
import os
from datetime import datetime

@Pyro4.expose
class ProcessingServer(object):
    def __init__(self):
        self.frame_count = 0
        self.output_dir = os.path.join(os.path.dirname(__file__), '../output')
        os.makedirs(self.output_dir, exist_ok=True)

    def process_frame(self, frame_base64):
        try:
            self.frame_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_data = base64.b64decode(frame_base64)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return {"status": "error", "message": "No se pudo decodificar la imagen"}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)

            img_name = f"frame_{self.frame_count}_{timestamp}.jpg"
            edge_name = f"edges_{self.frame_count}_{timestamp}.jpg"
            img_path = os.path.join(self.output_dir, img_name)
            edge_path = os.path.join(self.output_dir, edge_name)
            
            cv2.imwrite(img_path, img)
            cv2.imwrite(edge_path, edges)

            print(f"[OK] Frame #{self.frame_count} procesado")
            
            return {
                "status": "success",
                "frame_id": self.frame_count,
                "image_path": img_path,
                "edges_path": edge_path,
                "resolution": f"{img.shape[1]}x{img.shape[0]}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_frame_count(self):
        return self.frame_count

    def get_status(self):
        return {"status": "online", "service": "edge.processing"}

def main():
    host_ip = os.getenv("EDGE_SERVER_IP", "localhost")
    daemon = Pyro4.Daemon(host=host_ip, port=9091)
    ns = Pyro4.locateNS(host=host_ip, port=9090)
    
    server = ProcessingServer()
    uri = daemon.register(server, "edge.processing")
    ns.register("edge.processing", uri)
    
    print(f"[OK] Processing Server activo en {host_ip}:9091")
    daemon.requestLoop()

if __name__ == "__main__":
    main()