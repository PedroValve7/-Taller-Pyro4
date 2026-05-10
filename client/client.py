#!/usr/bin/env python3
# pyrefly: ignore [missing-import]
import Pyro4
# pyrefly: ignore [missing-import]
import cv2
import base64
import json
import os
from datetime import datetime
import time
import urllib.request
# pyrefly: ignore [missing-import]
import numpy as np

Pyro4.config.COMMTIMEOUT = 120

class EdgeClient:
    def __init__(self, camera_url=None):
        # Lee la IP de la cámara de la variable de entorno
        cam_ip = os.getenv("EDGE_CAMERA_IP", "192.168.18.14")
        self.camera_url = camera_url or f"http://{cam_ip}:8080/video"
        self.cap = None
        self.processing_server = None
        self.ai_server = None
        self.is_ip_webcam = False
        self.shot_url = None
        self.output_dir = os.path.join(os.path.dirname(__file__), '../output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def connect_servers(self):
        try:
            # Lee la IP del servidor de la variable de entorno
            host_pc = os.getenv("EDGE_SERVER_IP", "localhost")
            print(f"Conectando con servidores en {host_pc}...")
            ns = Pyro4.locateNS(host=host_pc, port=9090)
            
            self.processing_server = Pyro4.Proxy(ns.lookup("edge.processing"))
            self.ai_server = Pyro4.Proxy(ns.lookup("edge.ai"))
            
            # Verificar estado
            self.processing_server.get_status()
            self.ai_server.get_status()
            print("[OK] Servidores conectados\n")
            return True
        except Exception as e:
            print(f"[X] Error conectando servidores: {e}")
            return False
    
    def connect_camera(self):
        print(f"Conectando con cámara: {self.camera_url}")
        self.is_ip_webcam = "http" in self.camera_url and "/video" in self.camera_url
        if self.is_ip_webcam:
            self.shot_url = self.camera_url.replace("/video", "/shot.jpg")
            return True

        if self.camera_url.isdigit():
            self.cap = cv2.VideoCapture(int(self.camera_url))
        else:
            self.cap = cv2.VideoCapture(self.camera_url, cv2.CAP_FFMPEG)
        return self.cap.isOpened()
    
    def capture_frame(self):
        try:
            if self.is_ip_webcam:
                req = urllib.request.urlopen(self.shot_url, timeout=5)
                arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
                frame = cv2.imdecode(arr, -1)
            else:
                success, frame = self.cap.read()
                if not success: return None, None
            
            frame = cv2.resize(frame, (320, 240))
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            return frame_base64, frame
        except Exception:
            return None, None

    def process_and_analyze(self, frame_base64, analysis_type="security"):
        try:
            print("    [1/2] Procesando...")
            proc_result = self.processing_server.process_frame(frame_base64)
            print("    [2/2] Analizando con IA...")
            ai_result = self.ai_server.analyze_image(frame_base64, analysis_type)
            
            return {
                "status": "success",
                "processing": proc_result,
                "ai_analysis": ai_result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def run_continuous(self, interval=5, max_frames=50):
        print(f"EJECUTANDO: {interval}s entre frames\n")
        frame_count = 0
        try:
            while frame_count < max_frames or max_frames == 0:
                frame_count += 1
                print(f"--- Frame {frame_count} ---")
                frame_base64, frame = self.capture_frame()
                if frame is not None:
                    cv2.imshow("Smart Edge Hub", frame)
                    cv2.waitKey(1)
                    res = self.process_and_analyze(frame_base64)
                    if res["status"] == "success":
                        print(f"  [OK] IA: {res['ai_analysis']['result'][:100]}...")
                    else:
                        print(f"  [X] Error: {res['message']}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nDetenido.")
        finally:
            if self.cap: self.cap.release()
            cv2.destroyAllWindows()

def main():
    client = EdgeClient()
    if client.connect_servers() and client.connect_camera():
        client.run_continuous(interval=5, max_frames=50)

if __name__ == "__main__":
    main()
