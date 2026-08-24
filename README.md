# 🛡️ Mini-IDS: Sistema de Detección de Intrusos en Red

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Scapy](https://img.shields.io/badge/Scapy-2.5+-150458.svg)
![Cybersecurity](https://img.shields.io/badge/Cybersecurity-Blue_Team-shield.svg)
![Networking](https://img.shields.io/badge/Networking-TCP%2FIP-success.svg)

Un Sistema de Detección de Intrusos (IDS) ligero y autónomo escrito en Python. Esta herramienta monitoriza el tráfico de red en la capa de transporte (Capa 4 del modelo OSI) para identificar y alertar sobre patrones de ataque en tiempo real, específicamente **escaneos de puertos sigilosos (Stealth SYN Scans)** típicamente ejecutados por herramientas de auditoría como Nmap.

---

## 🚀 Características Principales

- **Detección de Escaneos SYN:** Analiza las banderas (flags) de los paquetes TCP buscando intentos de inicio de conexión (`S` / SYN) masivos que no completan el saludo de tres vías (3-way handshake).
- **Lógica de Umbrales Temporales:** Utiliza ventanas de tiempo dinámicas para evitar falsos positivos. (Ej. Alerta si una misma IP toca más de 15 puertos distintos en menos de 5 segundos).
- **Modo Simulación (In-Memory):** Incluye un módulo de inyección de paquetes para probar la lógica de detección en entornos CI/CD o sistemas Windows sin necesidad de instalar controladores de captura cruda (Raw Sockets / Npcap).
- **Bajo Consumo de Recursos:** No almacena el tráfico en memoria (parámetro `store=0`), procesando y descartando los paquetes al vuelo para evitar bloqueos por saturación de RAM.

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python
- **Manipulación de Red:** [Scapy](https://scapy.net/) (Lectura, disección y forjado de paquetes de red).

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone [https://github.com/TU_USUARIO/mini-ids.git](https://github.com/TU_USUARIO/mini-ids.git)
cd mini-ids
```

### 2. Instalar dependencias

Se recomienda utilizar un entorno virtual. Solo necesitas la librería Scapy:
```bash
pip install scapy
```
### 3. Requisitos del Sistema Operativo (Para el modo de Escucha Real)
- Linux: Se requiere ejecutar el script con privilegios sudo.
- Windows: Es indispensable tener instalado el controlador Npcap (marcando la compatibilidad con WinPcap) para permitir a Python leer la tarjeta de red en modo promiscuo.

## 🖥️ Uso de la Aplicación
El script tiene dos modos de funcionamiento configurables al final del archivo `mini_ids.py`:

### Modo 1: Simulación de Ataque (Por defecto)
Ideal para validar el código inmediatamente sin configurar tarjetas de red. El script forjará paquetes TCP maliciosos en memoria y los inyectará en el motor de análisis.

```bash
python mini_ids.py
```
Salida esperada: Verás una alerta crítica saltando al detectar los paquetes inyectados.

### Modo 2: Escucha de Tráfico Real
Para monitorizar tu red local, comenta la llamada a `simular_ataque_fuerza_bruta()` y descomenta el bloque de `sniff()` al final del código.
Ejecuta el script con privilegios de administrador:
```bash
# En Linux
sudo python mini_ids.py

# En Windows (ejecutar PowerShell como Administrador)
python mini_ids.py
```
Para probarlo en modo real, puedes lanzar un escaneo desde otra terminal o equipo hacia tu máquina:
```bash
nmap -sS -p 1-100 <TU_IP_LOCAL>
```

## 🧠 ¿Cómo funciona por debajo?
El motor de detección, implementado en `analizar_paquete()`, sigue este flujo lógico:
- Intercepta el paquete en crudo mediante un hook de Scapy.
- Disecciona las capas IP y TCP.
- Si el paquete tiene la bandera SYN activa, registra el timestamp y el puerto destino en un defaultdict.
- Evalúa si el historial reciente de esa IP (limpiando registros más antiguos que la ventana de tiempo definida) supera el umbral crítico de puertos únicos visitados.
- Si supera el umbral, bloquea lógicamente la IP en un set() para evitar spam de notificaciones y emite la alerta crítica.

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Siguientes pasos propuestos para ampliar el proyecto:
- [ ] Módulo de detección de ARP Spoofing (Man-in-the-Middle).
- [ ] Integración automática con Firewall (Iptables / Windows Defender) para bloquear IPs atacantes al instante.
- [ ] Exportación de logs a formato JSON para integración con SIEMs (Kibana / Splunk).

## 📄 Licencia
Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](https://github.com/MLPerarnau/Mini-IDS-Sistema-de-Detecci-n-de-Intrusos-en-Red/edit/main/LICENSE) para más detalles.
