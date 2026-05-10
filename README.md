# README - THYONI TECH: Visual Security Guard

## Descripción Rápida

**THYONI TECH: Visual Security Guard** es un sistema de vigilancia inteligente distribuido que captura video desde un teléfono móvil, lo procesa localmente y lo analiza con IA multimodal (Gemini), todo coordinado a través de Pyro4 (RPC distribuida).

## Estructura del Proyecto

```
SmartEdgeHub/
├── requirements.txt          # Dependencias Python
├── setup.py                  # Script de instalación
│
├── servers/                  # Componentes del servidor
│   ├── nameserver.py         # Pyro4 Nameserver (puerto 9090)
│   ├── processing_server.py  # Procesamiento local (puerto 9091)
│   └── ai_server.py          # IA + Gemini (puerto 9092)
│
├── client/                   # Cliente y pruebas
│   ├── client.py             # Cliente principal
│   └── test_client.py        # Cliente de prueba (sin cámara real)
│
├── output/                   # Directorio de salida
│   ├── frame_*.jpg           # Imágenes originales
│   ├── edges_*.jpg           # Imágenes procesadas
│   └── result_*.json         # Reportes de análisis
│
└── docs/                     # Documentación
    ├── PROPUESTA.md          # Descripción del proyecto
    └── ARQUITECTURA.md       # Diagrama de arquitectura
```

## Requisitos Previos

- Python 3.8 o superior
- Acceso a Google Gemini API (obtén tu key en https://ai.google.dev/)
- Red local (PC y móvil en la misma red - solo si usas cámara real)
- IP Webcam app en móvil (opcional - para captura real)

## Instalación Rápida

### 1. Instalar Dependencias
```bash
python setup.py
```

### 2. Configurar Gemini API
```bash
# Windows PowerShell
$env:GEMINI_API_KEY='tu-api-key-aqui'

# Linux/Mac
export GEMINI_API_KEY='tu-api-key-aqui'
```

## Ejecución

### Opción A: PRUEBA RÁPIDA (Sin cámara real)

**Terminal 1 - Nameserver:**
```bash
cd servers
python nameserver.py
```

**Terminal 2 - Processing Server:**
```bash
cd servers
python processing_server.py
```

**Terminal 3 - AI Server:**
```bash
cd servers
$env:GEMINI_API_KEY='tu-api-key-aqui'
python ai_server.py
```

**Terminal 4 - Cliente (Prueba):**
```bash
cd client
python test_client.py
```

### Opción B: CON CÁMARA REAL

1. Descargar e instalar **IP Webcam** en el móvil (desde Play Store)
2. Abrir la app y anotar la URL (ej: http://192.168.18.14:8080/video)
3. La URL ya está configurada en `client/client.py`: `camera_url = "http://192.168.18.14:8080/video"`
4. Ejecutar los mismos servidores que en Opción A
5. En Terminal 4:
```bash
cd client
python client.py
```

## Componentes

### Processing Server
- **Puerto:** 9091
- **Responsabilidad:** Procesar imágenes (filtros, guardado)
- **Entrada:** frame en base64
- **Salida:** metadatos + imagen guardada

### AI Server
- **Puerto:** 9092
- **Responsabilidad:** Análisis multimodal con Gemini
- **Modelos:** gemini-flash (Gemini API)
- **Entrada:** frame + prompt de análisis
- **Salida:** análisis de IA en texto

### Tipos de Análisis
- `"security"` - Detección de intrusos y anomalías
- `"description"` - Descripción completa del contenido
- `"anomaly"` - Identificación de comportamientos raros

## Salida

Los resultados se guardan en `output/`:

```json
{
  "frame_number": 1,
  "processing": {
    "status": "success",
    "frame_id": 1,
    "image_path": "output/frame_1_20260508_120000.jpg",
    "edges_path": "output/edges_1_20260508_120000.jpg"
  },
  "ai_analysis": {
    "status": "success",
    "analysis_type": "security",
    "result": "En la imagen se puede observar..."
  },
  "timestamp": "2026-05-08T12:00:00..."
}
```

## Arquitectura

```
Móvil (Cámara)
    ↓
Cliente Python (Captura + Orquesta)
    ↓
Pyro4 Nameserver (Registro de servicios)
    ├─→ Processing Server (OpenCV + guardado)
    └─→ AI Server (Gemini API)
        ↓
    output/ (Imágenes + reportes JSON)
```

## Características Destacadas

✅ **Arquitectura Distribuida** - Pyro4 RPC con Nameserver  
✅ **Multimodal IA** - Análisis de imágenes + texto con Gemini  
✅ **Edge Computing** - Procesamiento local antes de IA  
✅ **Serialización Eficiente** - Base64 para transmisión segura  
✅ **Manejo de Excepciones** - Recuperación ante fallos  
✅ **Escalable** - Agregar más servers/clientes fácilmente  
✅ **Documentado** - Propuesta + Arquitectura + Código comentado  

## Troubleshooting

| Problema | Solución |
|----------|----------|
| "No se pudo conectar con Nameserver" | Ejecuta nameserver.py primero |
| "edge.processing not found" | Ejecuta processing_server.py |
| "GEMINI_API_KEY not configured" | Establece: `$env:GEMINI_API_KEY='key'` |
| "No se pudo abrir la cámara" | Usa `test_client.py` o verifica URL IP Webcam |
| "CommunicationError" | Verifica que todos los servidores estén activos |

## Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|----------|
| Pyro4 | 4.82 | RPC Distribuida |
| Google Generativeai | >=0.5.4 | Gemini API (Soporte 1.5 Flash) |
| OpenCV | 4.8.0 | Procesamiento de imágenes |
| Python | 3.8+ | Lenguaje principal |

## Criterios de Evaluación Cumplidos

✅ **Conectividad:** Comunicación RPC Pyro4 entre múltiples nodos  
✅ **Robustez:** Manejo de excepciones, reconexión automática  
✅ **Creatividad:** Sistema completo de vigilancia con IA  
✅ **Claridad:** Código documentado + diagramas de arquitectura  
✅ **Multimodal IA:** Análisis de imagen + prompts con Gemini  
✅ **Capas Tecnológicas:** Edge (móvil) + Middleware (Pyro4) + Cloud (IA)  

## Contacto y Soporte

Para preguntas o problemas, revisa:
- `docs/PROPUESTA.md` - Descripción completa del proyecto
- `docs/ARQUITECTURA.md` - Detalles técnicos y diagramas
- Código comentado en `servers/` y `client/`

---

**Versión:** 1.0  
**Fecha:** Mayo 2026  
**Autores:** Proyecto de Computación Distribuida
