#!/usr/bin/env python3
"""
Cliente de Prueba - Simula capturas sin necesidad de cámara real
Útil para testing de la arquitectura distribuida
"""
# pyrefly: ignore [missing-import]
import Pyro4
Pyro4.config.COMMTIMEOUT = 120
import json
import os
import base64
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import cv2
from datetime import datetime
from client import EdgeClient

def generate_test_frame(frame_num):
    """Genera un frame de prueba (imagen sintética)"""
    # Crear imagen de 640x480 con contenido aleatorio
    img = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    
    # Agregar texto
    cv2.putText(img, f"Test Frame {frame_num}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Dibujar formas
    cv2.rectangle(img, (100, 150), (300, 350), (0, 255, 255), 2)
    cv2.circle(img, (500, 200), 50, (255, 0, 0), 3)
    
    # Codificar a base64
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return frame_base64

def test_distributed_system():
    """Prueba el sistema distribuido completo"""
    print("\n" + "=" * 60)
    print("PRUEBA DEL SISTEMA DISTRIBUIDO")
    print("=" * 60 + "\n")
    
    try:
        # Conectar con nameserver
        print("Conectando con Nameserver...")
        # Ajustado a tu IP real para consistencia con los servidores
        ns = Pyro4.locateNS(host="192.168.18.11", port=9090)
        print("[OK] Conectado\n")
        
        # Obtener referencias a servidores
        print("Localizando servidores...")
        processing_server = Pyro4.Proxy(ns.lookup("edge.processing"))
        ai_server = Pyro4.Proxy(ns.lookup("edge.ai"))
        print("[OK] Servidores encontrados\n")
        
        # Verificar estado
        print("Estado de servidores:")
        proc_status = processing_server.get_status()
        ai_status = ai_server.get_status()
        print(f"  Procesamiento: {json.dumps(proc_status, indent=4)}")
        print(f"  IA: {json.dumps(ai_status, indent=4)}\n")
        
        # Generar y procesar frames de prueba
        output_dir = os.path.join(os.path.dirname(__file__), '../output')
        os.makedirs(output_dir, exist_ok=True)
        
        print("=" * 60)
        print("PROCESANDO FRAMES DE PRUEBA")
        print("=" * 60 + "\n")
        
        for i in range(1, 4):
            print(f"\n--- Frame de Prueba {i} ---")
            
            # Generar frame sintético
            frame_base64 = generate_test_frame(i)
            print(f"[OK] Frame generado (tamaño: {len(frame_base64)} bytes base64)")
            
            # Enviar a procesamiento
            print("Enviando a servidor de procesamiento...")
            proc_result = processing_server.process_frame(frame_base64)
            if proc_result["status"] == "success":
                print(f"[OK] Frame procesado (ID: {proc_result['frame_id']})")
                print(f"  Archivo: {proc_result['image_path']}")
            else:
                print(f"[X] Error: {proc_result['message']}")
                continue
            
            # Enviar a IA
            print("Enviando a servidor de IA para análisis...")
            ai_result = ai_server.analyze_image(frame_base64, analysis_type="description")
            if ai_result["status"] == "success":
                print(f"[OK] Análisis completado")
                print(f"  Resultado: {ai_result['result'][:150]}...")
            else:
                print(f"[X] Error: {ai_result['message']}")
                continue
            
            # Guardar resultado combinado
            combined = {
                "frame_number": i,
                "processing": proc_result,
                "ai_analysis": ai_result,
                "timestamp": datetime.now().isoformat()
            }
            
            result_file = os.path.join(output_dir, f"test_result_{i}.json")
            with open(result_file, 'w') as f:
                json.dump(combined, f, indent=2, ensure_ascii=False)
            print(f"  Resultado guardado: {result_file}")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("RESUMEN DE PRUEBA")
        print("=" * 60)
        print(f"Frames procesados: {processing_server.get_frame_count()}")
        print(f"Análisis realizados: {ai_server.get_analysis_count()}")
        print("[OK] Sistema distribuido funcionando correctamente")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"[X] Error: {e}")
        print("\nAsegúrate de que los servidores estén ejecutándose:")
        print("  1. python nameserver.py")
        print("  2. python processing_server.py")
        print("  3. python ai_server.py")

if __name__ == "__main__":
    test_distributed_system()
