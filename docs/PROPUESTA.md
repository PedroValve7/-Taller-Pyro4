# PROPUESTA: VISUAL SECURITY GUARD
## Smart Edge Hub con IA Multimodal

---

## 1. PROBLEMA Y CASO DE USO

### Nombre del Proyecto
**Visual Security Guard** - Sistema de Vigilancia Inteligente Distribuido

### Problema
Los sistemas de vigilancia tradicionales generan volúmenes masivos de video que son difíciles de monitorear y analizar en tiempo real. Necesitamos una solución que:

1. **Capture** video del entorno mediante dispositivos móviles (Edge)
2. **Procese** localmente las imágenes para optimizar ancho de banda
3. **Analice** con IA las anomalías, intrusos y eventos sospechosos
4. **Genere** reportes automáticos y alertas
5. **Distribuya** la carga de procesamiento entre múltiples nodos

### Solución Propuesta
Sistema distribuido que captura video mediante teléfono móvil, lo procesa en un servidor local (Edge) y lo analiza con IA multimodal (Gemini) en un servidor remoto, generando reportes en tiempo real.

---

## 2. ARQUITECTURA DEL SISTEMA

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPAS DEL SISTEMA                        │
└─────────────────────────────────────────────────────────────┘

1. CAPA DE SENSADO (Mobile Edge)
   └─ Teléfono móvil con cámara
   └─ IP Webcam o similar
   └─ Stream de video en vivo

2. CAPA DE COMUNICACIÓN (Middleware)
   └─ Pyro4 Nameserver (Puerto 9090)
   └─ Objetos remotos registrados
   └─ Serialización de datos (base64)

3. CAPA DE PROCESAMIENTO LOCAL (Edge Server)
   └─ Servidor de Procesamiento Local (Puerto 9091)
   └─ Aplicación de filtros OpenCV
   └─ Almacenamiento de imágenes
   └─ Serialización frame → base64

4. CAPA DE IA (Cloud/Local)
   └─ Servidor de IA (Puerto 9092)
   └─ Integración con Gemini API
   └─ Análisis multimodal (imagen + prompt)
   └─ Generación de reportes
```

### Flujo de Datos

```
Móvil (Cámara)
    │
    ├─ Captura frame
    │
    └─► Cliente Python
         │
         ├─ Codifica a base64
         │
         └─► Pyro4 Nameserver
              │
              ├─► Processing Server
              │    ├─ Aplica filtros
              │    ├─ Guarda imagen
              │    └─ Retorna metadata
              │
              └─► AI Server
                   ├─ Recibe imagen base64
                   ├─ Envía a Gemini API
                   ├─ Analiza contenido
                   └─ Retorna reporte
```

---

## 3. DEFINICIÓN DE INTERFACES

### 3.1 Processing Server (`edge.processing`)

**Métodos Expuestos:**

```python
@Pyro4.expose
def process_frame(frame_base64: str) -> dict:
    """
    Procesa un frame capturado
    
    Entrada:
        frame_base64: Imagen codificada en base64
    
    Retorna:
        {
            "status": "success|error",
            "frame_id": int,
            "timestamp": str,
            "image_path": str,
            "edges_path": str,
            "resolution": str
        }
    """

@Pyro4.expose
def get_frame_count() -> int:
    """Retorna número total de frames procesados"""

@Pyro4.expose
def get_status() -> dict:
    """Retorna estado del servidor"""
```

### 3.2 AI Server (`edge.ai`)

**Métodos Expuestos:**

```python
@Pyro4.expose
def analyze_image(frame_base64: str, analysis_type: str) -> dict:
    """
    Analiza una imagen con IA
    
    Entrada:
        frame_base64: Imagen codificada en base64
        analysis_type: "security" | "description" | "anomaly"
    
    Retorna:
        {
            "status": "success|error",
            "analysis_id": int,
            "timestamp": str,
            "analysis_type": str,
            "result": str (texto del análisis Gemini)
        }
    """

@Pyro4.expose
def batch_analyze(frames_base64: list, analysis_type: str) -> list:
    """Analiza múltiples imágenes"""

@Pyro4.expose
def get_analysis_count() -> int:
    """Retorna número total de análisis realizados"""

@Pyro4.expose
def get_status() -> dict:
    """Retorna estado del servidor"""
```

---

## 4. DECISIONES DE DISEÑO

### 4.1 Uso de Pyro4
- ✅ **RPC distribuida** sin acoplamiento directo
- ✅ **Nameserver centralizado** para descubrimiento de servicios
- ✅ **Serialización automática** de objetos Python
- ✅ **Manejo transparente de red**

### 4.2 Serialización de Imágenes
- **Formato**: Base64 (compatible con cualquier transmisión de red)
- **Razón**: HTTP, Pyro4, y APIs REST requieren datos serializables
- **Ventaja**: Evita corrupción en transmisión de binarios

### 4.3 Separación de Responsabilidades
- **Processing Server**: Preprocesamiento local (filtros, guardado)
- **AI Server**: Análisis inteligente centralizado
- **Benefit**: Escalabilidad independiente de cada capa

### 4.4 Tipos de Análisis
- `security`: Detección de intrusos, objetos sospechosos
- `description`: Descripción general del contenido
- `anomaly`: Identificación de comportamientos inusuales

---

## 5. MANEJO DE EXCEPCIONES

### Escenarios Cubiertos

1. **Falla de Nameserver**
   ```python
   try:
       ns = Pyro4.locateNS()
   except Exception:
       print("Nameserver no disponible")
   ```

2. **Móvil desconectado**
   ```python
   if cap.isOpened():
       ret, frame = cap.read()
   else:
       print("Cámara desconectada")
   ```

3. **Servidor caído**
   ```python
   try:
       result = server.method()
   except Pyro4.CommunicationError:
       print("Servidor no responde")
   ```

4. **Error en Gemini API**
   ```python
   try:
       response = model.generate_content(...)
   except Exception as e:
       return {"status": "error", "message": str(e)}
   ```

---

## 6. FLUJO DE EJECUCIÓN

### Paso 1: Iniciar Nameserver
```bash
python servers/nameserver.py
```
✓ Puerto 9090
✓ Centraliza registro de servicios

### Paso 2: Iniciar Servers
```bash
# Terminal 1
python servers/processing_server.py

# Terminal 2
$env:GEMINI_API_KEY='tu-api-key-aqui'
python servers/ai_server.py
```

### Paso 3: Ejecutar Cliente
```bash
# Prueba sin cámara real
python client/test_client.py

# Con cámara IP Webcam (actualizar URL)
python client/client.py
```

---

## 7. MÉTRICAS Y MONITOREO

### Contadores Implementados
- `processing_server.get_frame_count()`: Frames procesados
- `ai_server.get_analysis_count()`: Análisis realizados
- `get_status()`: Estado de cada servidor

### Salida Generada
- `output/frame_*.jpg`: Imágenes originales
- `output/edges_*.jpg`: Imágenes procesadas
- `output/result_*.json`: Reportes de análisis

---

## 8. TECNOLOGÍAS UTILIZADAS

| Componente | Tecnología | Propósito |
|---|---|---|
| **RPC Distribuida** | Pyro4 4.82 | Comunicación entre nodos |
| **IA Multimodal** | Google Gemini Flash | Análisis de imágenes |
| **Visión Computacional** | OpenCV 4.8.0 | Procesamiento de imágenes |
| **Serialización** | Base64 | Transmisión de datos |
| **Lenguaje** | Python 3.9+ | Desarrollo |

---

## 9. CONCLUSIÓN

Visual Security Guard demuestra una arquitectura distribuida robusta que:
✅ Captura desde Edge (móvil)
✅ Procesa localmente (ahorra ancho de banda)
✅ Analiza con IA (genera valor)
✅ Comunica vía RPC distribuida (sin acoplamiento)
✅ Escala horizontalmente (agregar más nodos)

Aplicable a: Vigilancia, domótica, monitoreo industrial, seguridad perimetral.
