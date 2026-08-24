from scapy.all import sniff, TCP, IP, ARP, Ether
from collections import defaultdict
import time
import json
import subprocess
import os
import requests

# --- CONFIGURACIÓN DEL UMBRAL ---
UMBRAL_PUERTOS = 15
VENTANA_TIEMPO_SEGUNDOS = 5

# --- CONFIGURACIÓN DE DISCORD ---
# Pega aquí la URL que copiaste de tu canal de Discord
DISCORD_WEBHOOK_URL = "" 

# --- ESTADO DE LA RED ---
registro_conexiones = defaultdict(list)
ips_bloqueadas = set()
mapa_mac_ip = {}  

def enviar_notificacion_discord(mensaje):
    """Envía un mensaje push al canal de Discord vía Webhook"""
    if not DISCORD_WEBHOOK_URL:
        return # Si no hay URL, saltamos este paso sin dar error
        
    payload = {
        "content": mensaje,
        "username": "Mini-IDS Alertas", 
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/8373/8373132.png" # Icono de un escudo policial
    }
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        print("   👾 Notificación enviada por Discord con éxito.")
    except Exception as e:
        print(f"   ❌ Error al enviar notificación a Discord: {e}")

def registrar_alerta_json(tipo_ataque, ip_atacante, detalles):
    """Guarda la alerta en un archivo JSON estructurado"""
    alerta = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_ataque": tipo_ataque,
        "ip_atacante": ip_atacante,
        "detalles": detalles
    }
    with open("alertas.json", "a") as f:
        f.write(json.dumps(alerta) + "\n")

def bloquear_ip_firewall(ip_atacante):
    """Ejecuta un comando en el sistema operativo para bloquear la IP"""
    print(f"🧱 [FIREWALL] Intentando bloquear la IP {ip_atacante}...")
    comando_win = f'netsh advfirewall firewall add rule name="MiniIDS_Block_{ip_atacante}" dir=in action=block remoteip={ip_atacante}'
    try:
        resultado = subprocess.run(comando_win, shell=True, capture_output=True, text=True)
        if "Acceso denegado" in resultado.stderr or resultado.returncode != 0:
            print("   ⚠️ No se pudo bloquear. (Se requieren permisos de Administrador).")
        else:
            print(f"   ✅ ¡IP {ip_atacante} bloqueada con éxito en Windows Defender!")
    except Exception as e:
        print(f"   ❌ Error al ejecutar el comando de firewall: {e}")

def analizar_paquete(paquete):
    """Evalúa cada paquete interceptado en busca de anomalías TCP y ARP"""
    
    # ==========================================
    # 1. DETECCIÓN DE ESCANEO DE PUERTOS (TCP)
    # ==========================================
    if paquete.haslayer(IP) and paquete.haslayer(TCP):
        ip_origen = paquete[IP].src
        puerto_destino = paquete[TCP].dport
        banderas_tcp = paquete[TCP].flags
        
        if banderas_tcp == 'S':
            tiempo_actual = time.time()
            if ip_origen in ips_bloqueadas: return

            registro_conexiones[ip_origen].append((tiempo_actual, puerto_destino))
            registro_conexiones[ip_origen] = [
                (t, p) for t, p in registro_conexiones[ip_origen] 
                if tiempo_actual - t <= VENTANA_TIEMPO_SEGUNDOS
            ]
            
            puertos_unicos = set(p for t, p in registro_conexiones[ip_origen])
            
            if len(puertos_unicos) >= UMBRAL_PUERTOS:
                print("\n" + "="*55)
                print(f"🚨 [ALERTA CRÍTICA] ESCANEO DE PUERTOS DETECTADO")
                print(f"   IP Atacante: {ip_origen}")
                print("="*55)
                
                ips_bloqueadas.add(ip_origen)
                registrar_alerta_json("Stealth SYN Scan", ip_origen, f"Tocó {len(puertos_unicos)} puertos en {VENTANA_TIEMPO_SEGUNDOS}s")
                
                # --- LANZAR NOTIFICACIÓN DISCORD ---
                mensaje_discord = f"🚨 **ALERTA DE SEGURIDAD - Mini IDS** 🚨\n\n**Tipo:** Escaneo de Puertos\n**Atacante:** `{ip_origen}`\n**Detalles:** {len(puertos_unicos)} puertos tocados en {VENTANA_TIEMPO_SEGUNDOS}s.\n\n🛡️ _Iniciando protocolo de bloqueo en Firewall..._"
                enviar_notificacion_discord(mensaje_discord)
                
                bloquear_ip_firewall(ip_origen)

    # ==========================================
    # 2. DETECCIÓN DE ARP SPOOFING (Man-in-the-Middle)
    # ==========================================
    if paquete.haslayer(ARP) and paquete[ARP].op == 2: 
        ip_origen = paquete[ARP].psrc
        mac_origen = paquete[ARP].hwsrc
        
        if ip_origen in mapa_mac_ip:
            if mapa_mac_ip[ip_origen] != mac_origen:
                print("\n" + "="*55)
                print(f"☠️ [ALERTA CRÍTICA] ARP SPOOFING DETECTADO")
                print(f"   La IP {ip_origen} cambió su MAC a {mac_origen}")
                print("="*55)
                
                registrar_alerta_json("ARP Spoofing / MITM", ip_origen, f"MAC modificada a {mac_origen}")
                
                # --- LANZAR NOTIFICACIÓN DISCORD ---
                mensaje_discord = f"☠️ **ALERTA CRÍTICA - Mini IDS** ☠️\n\n**Tipo:** ARP Spoofing (Man-in-the-Middle)\n**Red:** La IP `{ip_origen}` ha cambiado su MAC repentinamente a `{mac_origen}`.\n\n⚠️ _Posible interceptación de tráfico en la red local._"
                enviar_notificacion_discord(mensaje_discord)
                
                mapa_mac_ip[ip_origen] = mac_origen
        else:
            mapa_mac_ip[ip_origen] = mac_origen


def simulador_de_ataques():
    """Simula los ataques para probar las mejoras"""
    print("\n🚀 Iniciando Motor de Simulación (Escaneo TCP + ARP Spoofing)...\n")
    
    print("🕵️ Simulando conexión legítima del router...")
    analizar_paquete(ARP(op=2, psrc="192.168.1.1", hwsrc="00:11:22:33:44:55"))
    time.sleep(1)
    
    print("😈 Simulando atacante envenenando la tabla ARP...")
    analizar_paquete(ARP(op=2, psrc="192.168.1.1", hwsrc="AA:BB:CC:DD:EE:FF"))
    time.sleep(2)

    ip_atacante_tcp = "10.0.0.55"
    print(f"\n🕵️ Simulando escaneo silencioso desde {ip_atacante_tcp}...")
    for puerto in range(1, 21):
        analizar_paquete(IP(src=ip_atacante_tcp, dst="192.168.1.10") / TCP(dport=puerto, flags='S'))


if __name__ == "__main__":
    print("🛡️ Iniciando Mini-IDS Avanzado con Integración Discord...")
    simulador_de_ataques()
