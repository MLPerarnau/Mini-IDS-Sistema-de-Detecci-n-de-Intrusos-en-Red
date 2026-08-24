# 🛡️ Mini-IDS/IPS: Sistema de Detección y Prevención de Intrusos en Red

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Scapy](https://img.shields.io/badge/Scapy-2.5+-150458.svg)
![Cybersecurity](https://img.shields.io/badge/Cybersecurity-Blue_Team-shield.svg)
![Networking](https://img.shields.io/badge/Networking-TCP%2FIP-success.svg)

Un Sistema de Detección y Prevención de Intrusos (IDS/IPS) ligero y autónomo escrito en Python. Esta herramienta monitoriza el tráfico de red en la capa de enlace (Capa 2) y transporte (Capa 4) del modelo OSI para identificar, alertar y bloquear patrones de ataque en tiempo real.
---

## 🚀 Características Principales

- **Detección de Escaneos SYN:** Analiza las banderas (flags) de los paquetes TCP buscando intentos de inicio de conexión (`S` / SYN) masivos que no completan el saludo de tres vías (3-way handshake) típicos de Nmap.
- **Protección contra ARP Spoofing:** Detecta ataques *Man-in-the-Middle (MitM)* monitorizando cambios repentinos en las asignaciones IP-MAC de la red local.
- **Prevención Activa (IPS):** Bloqueo automático e instantáneo de las IPs atacantes modificando las reglas de Windows Defender Firewall mediante comandos nativos (`netsh`).
- **Integración SIEM (JSON):** Exporta las alertas generadas automáticamente a un archivo estructurado `alertas.json`, listo para ser ingerido por sistemas como Elastic Stack (ELK), Splunk o Logstash.
- **Modo Simulación (In-Memory):** Incluye un módulo de inyección de paquetes para probar la lógica de detección en entornos CI/CD o sistemas Windows sin necesidad de instalar controladores de captura cruda (Raw Sockets / Npcap).

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python
- **Manipulación de Red:** [Scapy](https://scapy.net/) (Lectura, disección y forjado de paquetes de red).
- **Interacción OS:** Módulo `subprocess` para comunicación directa con el Firewall nativo.

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

Windows: Es indispensable tener instalado el controlador Npcap (marcando la compatibilidad con WinPcap) para permitir a Python leer la tarjeta de red en modo promiscuo. Se requieren privilegios de Administrador para que la mitigación automática del Firewall funcione.

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
El motor de detección, implementado en analizar_paquete(), sigue este flujo lógico:
- Capa 4 (TCP): Intercepta el paquete en crudo, disecciona las capas y busca la bandera SYN activa. Evalúa si el historial reciente de esa IP supera el umbral crítico de puertos únicos en una ventana de tiempo (limpiando registros antiguos).

- Capa 2 (ARP): Verifica paquetes ARP Reply (op=2) y mantiene un mapeo en memoria de las direcciones físicas. Si una IP legítima cambia bruscamente de MAC, dispara la alerta de envenenamiento ARP.

- Mitigación: Al confirmar una amenaza, la IP es aislada en una lista negra en memoria, se emite una alerta JSON y se invoca un subproceso del sistema operativo para bloquear la amenaza en el Firewall.

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Siguientes pasos propuestos para ampliar el proyecto:
- [x] Módulo de detección de ARP Spoofing (Man-in-the-Middle).

- [x] Integración automática con Firewall (Windows Defender) para bloquear IPs atacantes al instante.

- [x] Exportación de logs a formato JSON para integración con SIEMs.

- [ ] Soporte nativo de IPS para iptables / ufw en sistemas Linux.

- [ ] Envío de notificaciones de alerta en tiempo real vía bot de Telegram o webhook de Slack.

## 📄 Licencia
Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](https://github.com/MLPerarnau/Mini-IDS-Sistema-de-Detecci-n-de-Intrusos-en-Red/edit/main/LICENSE) para más detalles.
