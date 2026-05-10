# DIAGRAMA DE ARQUITECTURA
## Visual Security Guard - Distributed System

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                     SMART EDGE HUB - VISUAL SECURITY GUARD               ║
║                         Computación Distribuida con IA                    ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAPA 1: SENSADO (EDGE MOBILE)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────────────┐                                                  │
│   │  Teléfono Móvil      │                                                  │
│   │  ┌──────────────┐    │                                                  │
│   │  │   Cámara     │    │                                                  │
│   │  └──────────────┘    │                                                  │
│   │        │ (stream)    │                                                  │
│   │        ▼             │                                                  │
│   │  ┌──────────────┐    │                                                  │
│   │  │ IP Webcam    │    │                                                  │
│   │  │ :8080/video  │    │                                                  │
│   │  └──────────────┘    │                                                  │
│   └──────────────────────┘                                                  │
│        │ (HTTP Stream)                                                      │
│        │ 192.168.1.100:8080                                                 │
│        │                                                                    │
│        ▼                                                                    │
│   ┌──────────────────────┐                                                  │
│   │   Cliente Python     │                                                  │
│   │   (PC/Laptop)        │                                                  │
│   │                      │                                                  │
│   │ • Capture frames     │                                                  │
│   │ • Encode to base64   │                                                  │
│   │ • Orchestrate RPC    │                                                  │
│   └──────────────────────┘                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                   CAPA 2: COMUNICACIÓN (MIDDLEWARE - PYRO4)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│              ┌──────────────────────────────────────────┐                   │
│              │   Pyro4 Nameserver (localhost:9090)     │                   │
│              │                                          │                   │
│              │  Registro de Objetos Remotos:            │                   │
│              │  • edge.processing  ──► Processing Srv  │                   │
│              │  • edge.ai          ──► AI Server       │                   │
│              └──────────────────────────────────────────┘                   │
│                         ▲                                                   │
│                         │ RPC Calls                                         │
│       ┌─────────────────┼─────────────────┐                                 │
│       │                 │                 │                                 │
│       ▼                 ▼                 ▼                                 │
│   ┌────────────┐   ┌──────────┐   ┌───────────┐                           │
│   │  Cliente   │   │Processing│   │  AI Server│                           │
│   │  Python    │   │  Server  │   │  (Gemini) │                           │
│   │            │   │          │   │           │                           │
│   └────────────┘   └──────────┘   └───────────┘                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│              CAPA 3: PROCESAMIENTO LOCAL (EDGE SERVER)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────┐        │
│   │  Processing Server (localhost:9091)                          │        │
│   │  ┌─────────────────────────────────────────────────────────┐ │        │
│   │  │  Entrada: frame_base64 (HTTP Stream → base64)          │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  1. Decodificar (base64 → numpy array)                │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  2. Conversión a escala de grises                      │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  3. Aplicar filtros (Gauss, Canny edges)              │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  4. Guardar en disco                                    │ │        │
│   │  │     ├─ frame_N_timestamp.jpg                           │ │        │
│   │  │     └─ edges_N_timestamp.jpg                           │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  5. Retornar metadata (path, resolución, etc)          │ │        │
│   │  │                                                         │ │        │
│   │  │  Métodos Expuestos:                                     │ │        │
│   │  │  • process_frame(frame_base64) → dict                  │ │        │
│   │  │  • get_frame_count() → int                             │ │        │
│   │  │  • get_status() → dict                                 │ │        │
│   │  └─────────────────────────────────────────────────────────┘ │        │
│   │                                                              │        │
│   │  Salida: {status, frame_id, timestamp, image_path, ...}     │        │
│   │                                                              │        │
│   └───────────────────────────────────────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    CAPA 4: IA MULTIMODAL (CLOUD/LOCAL)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌───────────────────────────────────────────────────────────────┐        │
│   │  AI Server (localhost:9092)                                  │        │
│   │  ┌─────────────────────────────────────────────────────────┐ │        │
│   │  │  Entrada: frame_base64 + analysis_type                 │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  1. Decodificar image_base64 → bytes                   │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  2. Seleccionar prompt según analysis_type:             │ │        │
│   │  │     ├─ "security":  Detectar intrusos/anomalías        │ │        │
│   │  │     ├─ "description": Describir contenido              │ │        │
│   │  │     └─ "anomaly": Identificar comportamientos raros    │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  3. Enviar a Gemini API:                                │ │        │
│   │  │     ├─ image (bytes)                                    │ │        │
│   │  │     └─ prompt (texto)                                   │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │    ┌──────────────────────────────────┐                │ │        │
│   │  │    │   Google Generative AI (Gemini)  │                │ │        │
│   │  │    │   API Key: GEMINI_API_KEY        │                │ │        │
│   │  │    │   Model: gemini-flash (Gemini)   │                │ │        │
│   │  │    │   - Procesa imagen + texto       │                │ │        │
│   │  │    │   - Devuelve análisis (IA)       │                │ │        │
│   │  │    └──────────────────────────────────┘                │ │        │
│   │  │     │                                                   │ │        │
│   │  │     ▼                                                   │ │        │
│   │  │  4. Retornar resultado del análisis                    │ │        │
│   │  │                                                         │ │        │
│   │  │  Métodos Expuestos:                                     │ │        │
│   │  │  • analyze_image(frame_base64, type) → dict            │ │        │
│   │  │  • batch_analyze(frames, type) → list                  │ │        │
│   │  │  • get_analysis_count() → int                          │ │        │
│   │  │  • get_status() → dict                                 │ │        │
│   │  └─────────────────────────────────────────────────────────┘ │        │
│   │                                                              │        │
│   │  Salida: {status, analysis_id, timestamp, result (IA), ...} │        │
│   │                                                              │        │
│   └───────────────────────────────────────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    CAPA 5: ALMACENAMIENTO Y SALIDA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   output/                                                                   │
│   ├── frame_1_20260508_120000.jpg          (Imagen original)               │
│   ├── edges_1_20260508_120000.jpg          (Imagen procesada)              │
│   ├── result_1_20260508_120000.json        (Análisis completo)             │
│   ├── frame_2_20260508_120002.jpg                                          │
│   ├── edges_2_20260508_120002.jpg                                          │
│   ├── result_2_20260508_120002.json                                        │
│   └── ...                                                                   │
│                                                                              │
│   Estructura JSON de result_N.json:                                         │
│   {                                                                         │
│     "processing": {                                                        │
│       "status": "success",                                                 │
│       "frame_id": 1,                                                       │
│       "image_path": "output/frame_1_....jpg",                             │
│       "edges_path": "output/edges_1_....jpg"                              │
│     },                                                                     │
│     "ai_analysis": {                                                       │
│       "status": "success",                                                 │
│       "analysis_type": "security",                                         │
│       "result": "[Análisis de Gemini aquí]"                                │
│     }                                                                      │
│   }                                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║                        FLUJO COMPLETO DE DATOS                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

1. CAPTURA (Móvil)
   Teléfono → IP Webcam :8080/video → H.264 stream

2. SERIALIZACIÓN (Cliente)
   Stream → OpenCV → frame → JPEG encoding → base64 string

3. COMUNICACIÓN RPC (Pyro4)
   Cliente → Nameserver → lookup("edge.processing")
   Cliente → Processing Server (RPC)
   Cliente → Nameserver → lookup("edge.ai")
   Cliente → AI Server (RPC)

4. PROCESAMIENTO (Processing Server)
   base64 → decode → OpenCV filters → save to disk → return metadata

5. ANÁLISIS IA (AI Server)
   base64 → Gemini API → multimodal analysis → return text

6. ORQUESTACIÓN (Cliente)
   Para cada frame:
     1. process_frame() → Procesar
     2. analyze_image() → Analizar
     3. Guardar resultado JSON
     4. Esperar intervalo
     5. Siguiente frame

╔═══════════════════════════════════════════════════════════════════════════╗
║                      MANEJO DE CONCURRENCIA                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

• Pyro4 maneja threading automáticamente para múltiples clientes
• Cada servidor acepta múltiples conexiones simultáneas
• No hay sincronización de estado compartido entre servidores
• Los contadores (frame_count, analysis_count) son seguros en Python
• Las imágenes guardadas se identifican con timestamp único

╔═══════════════════════════════════════════════════════════════════════════╗
║                         VENTAJAS DE LA ARQUITECTURA                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

✅ ESCALABILIDAD
   - Agregar más cámaras (nuevos clientes)
   - Agregar más processing servers
   - Agregar más AI servers

✅ RESILIENCIA
   - Si un server cae, otros siguen funcionando
   - Reconexión automática
   - Manejo de excepciones en cada RPC call

✅ SEPARACIÓN DE RESPONSABILIDADES
   - Processing Server: Optimización de ancho de banda
   - AI Server: Análisis inteligente
   - Escalable independientemente

✅ COMPATIBILIDAD
   - Base64 compatible con cualquier red
   - Pyro4 funciona sin cambios en Windows/Linux
   - Gemini API accesible desde cualquier lugar
```

---

## Notas sobre la Serialización

**¿Por qué Base64?**
- ✅ Transportable por RPC (Pyro4 serializa strings sin problemas)
- ✅ HTTP-safe (si se expone vía REST)
- ✅ Sin corrupción de bytes en transmisión
- ✅ Compatible con JSON
- ⚠️ Aumenta tamaño ~33% (trade-off aceptable)

**Alternativas (no usadas):**
- Guardar imagen en disco → pasar ruta: requiere NFS/Samba
- Bytes directos: Pyro4 lo maneja, pero menos seguro
- Compresión adicional: Complica la arquitectura
