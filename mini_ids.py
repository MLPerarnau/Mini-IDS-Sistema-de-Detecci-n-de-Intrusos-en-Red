from scapy.all import sniff, TCP, IP
from collections import defaultdict
import time

# --- CONFIGURACIÓN DEL UMBRAL ---
# Si una IP intenta conectar a más de X puertos distintos en Y segundos, salta la alerta.
UMBRAL_PUERTOS = 15
VENTANA_TIEMPO_SEGUNDOS = 5

# Diccionario para mantener el estado de las conexiones.
# Formato: { "192.168.1.50": [ (tiempo_1, puerto_A), (tiempo_2, puerto_B)... ] }
registro_conexiones = defaultdict(list)
ips_bloqueadas = set()  # Para no repetir alertas sobre la misma IP

def analizar_paquete(paquete):
    """
    Función de callback que evalúa cada paquete interceptado o simulado.
    """
    # Solo nos interesan paquetes IP y TCP
    if paquete.haslayer(IP) and paquete.haslayer(TCP):
        
        ip_origen = paquete[IP].src
        puerto_destino = paquete[TCP].dport
        banderas_tcp = paquete[TCP].flags
        
        # 'S' significa bandera SYN (inicio de conexión). 
        # Los escaneos sigilosos usan SYN sin llegar a completar el saludo de 3 vías.
        if banderas_tcp == 'S':
            tiempo_actual = time.time()
            
            # Si ya alertamos sobre esta IP, la ignoramos para no saturar la consola
            if ip_origen in ips_bloqueadas:
                return

            # Registramos el intento de conexión
            registro_conexiones[ip_origen].append((tiempo_actual, puerto_destino))
            
            # Limpiamos el historial viejo (fuera de nuestra ventana de tiempo)
            registro_conexiones[ip_origen] = [
                (t, p) for t, p in registro_conexiones[ip_origen] 
                if tiempo_actual - t <= VENTANA_TIEMPO_SEGUNDOS
            ]
            
            # Contamos cuántos puertos ÚNICOS ha tocado esta IP en la ventana de tiempo
            puertos_unicos = set(p for t, p in registro_conexiones[ip_origen])
            
            if len(puertos_unicos) >= UMBRAL_PUERTOS:
                print("\n" + "="*50)
                print(f"🚨 [ALERTA CRÍTICA] Posible ESCANEO DE PUERTOS detectado!")
                print(f"   IP Atacante: {ip_origen}")
                print(f"   Comportamiento: {len(puertos_unicos)} puertos distintos en < {VENTANA_TIEMPO_SEGUNDOS}s")
                print("="*50 + "\n")
                
                # Añadimos la IP a la lista de alertadas
                ips_bloqueadas.add(ip_origen)


def simular_ataque_fuerza_bruta():
    """
    Simula un escaneo de puertos inyectando paquetes directamente en la función
    de análisis, sin necesidad de usar la tarjeta de red (ideal para testing en Windows).
    """
    ip_atacante = "10.0.0.55"
    ip_destino = "192.168.1.10"
    
    print("\n🚀 Iniciando simulador de tráfico en memoria...")
    print(f"🕵️ Simulando escaneo silencioso desde {ip_atacante}...")
    
    # Simulamos un ataque enviando paquetes a 20 puertos diferentes
    for puerto in range(1, 21):
        # Fabricamos un paquete TCP idéntico al que enviaría Nmap
        paquete_falso = IP(src=ip_atacante, dst=ip_destino) / TCP(dport=puerto, flags='S')
        
        # Se lo inyectamos al analizador
        analizar_paquete(paquete_falso)
        
        # Pausa para simular latencia de red
        time.sleep(0.1)


if __name__ == "__main__":
    print("🛡️ Iniciando Mini-IDS (Sistema de Detección de Intrusos)...")
    
    # ---------------------------------------------------------
    # MODO 1: SIMULACIÓN (Activo por defecto para pruebas)
    # Ejecuta el escaneo falso en memoria para validar la lógica.
    # ---------------------------------------------------------
    simular_ataque_fuerza_bruta()

    # ---------------------------------------------------------
    # MODO 2: ESCUCHA REAL EN RED (Comentado)
    # Para usar esto en Windows necesitas instalar Npcap.
    # En Linux funciona nativamente ejecutando con 'sudo'.
    # ---------------------------------------------------------
    # print("👂 Escuchando tráfico de red (Presiona Ctrl+C para detener)")
    # try:
    #     sniff(prn=analizar_paquete, store=0)
    # except PermissionError:
    #     print("❌ Error de permisos: Este script necesita privilegios de Administrador o root.")
    # except Exception as e:
    #     print(f"❌ Error al iniciar la captura: {e}. ¿Falta Npcap en Windows?")