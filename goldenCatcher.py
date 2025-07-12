import json
import requests
from bs4 import BeautifulSoup
import random
import time

def verificar_talla_especifica(url, talla_a_buscar):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/533.36 (KHTML, like Gecko) Firefox/109.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/604.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    ]

    for attempt in range(3):
        selected_user_agent = random.choice(user_agents)
        headers = {
            'User-Agent': selected_user_agent,
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1'
        }
        
        print(f"DEBUG: Intento {attempt + 1}: Usando User-Agent: {selected_user_agent} para {url}")

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            html_content = response.text
            print(f"DEBUG: HTML descargado. Tamaño: {len(html_content)} caracteres.")

            soup = BeautifulSoup(html_content, 'html.parser')

            target_input = soup.find('input', attrs={
                'data-attr-id': 'size',
                'data-attr-value': str(talla_a_buscar),
            })

            if target_input:
                print(f"DEBUG: Input para la talla '{talla_a_buscar}' encontrado. ID: {target_input.get('id')}")
                

                input_classes = target_input.get('class', [])
                
                if 'notify-me-eligible-attribute' in input_classes:
                    print(f"DEBUG: Clase 'notify-me-eligible-attribute' encontrada en el input. Talla NO disponible.")
                    return False, f"La talla '{talla_a_buscar}' NO está disponible (requiere notificación)."
                else:
                    print(f"DEBUG: Clase 'notify-me-eligible-attribute' NO encontrada en el input. Talla SÍ disponible.")
                    return True, f"¡La talla '{talla_a_buscar}' está DISPONIBLE!"
            else:
                print(f"DEBUG: No se encontró el input para la talla '{talla_a_buscar}' en el HTML descargado. La talla puede no existir para este producto o el HTML recibido está incompleto.")
                return None, f"La talla '{talla_a_buscar}' no fue encontrada en las opciones del producto."

        except requests.exceptions.Timeout:
            print(f"DEBUG: Error: La solicitud a '{url}' ha excedido el tiempo límite. Reintentando...")
            time.sleep(random.uniform(2, 5))
            continue
        except requests.exceptions.HTTPError as e:
            print(f"DEBUG: Error HTTP al acceder a la página '{url}': {e.response.status_code} - {e.response.reason}. Reintentando...")
            if e.response and e.response.status_code == 403:
                print("DEBUG: Posiblemente bloqueado por el sitio web.")
            time.sleep(random.uniform(2, 5))
            continue
        except Exception as e:
            print(f"DEBUG: Ocurrió un error inesperado durante la obtención/análisis: {e}. Reintentando...")
            time.sleep(random.uniform(2, 5))
            continue

    return None, "Se agotaron los reintentos. No se pudo obtener ni verificar la talla debido a errores persistentes."


if __name__ == "__main__":
    print("Iniciando prueba local de monitoreo de tallas de zapatos en Golden Goose.")
    
    url_producto = "https://www.goldengoose.com/fr/fr/super-star-avec--toile-paillettes-bordeaux-et-contrefort-argent--cod-GWF00102.F004057.11372.html"
    

    talla_a_probar = "36" 

    print(f"\nURL del producto: {url_producto}")
    print(f"Talla a probar: {talla_a_probar}")

    disponible, mensaje_estado = verificar_talla_especifica(url_producto, talla_a_probar)

    if disponible is True:
        print(f"\n✨ ¡RESULTADO! {mensaje_estado}")
    elif disponible is False:
        print(f"\n⚠️ RESULTADO: {mensaje_estado}")
    else: 
        print(f"\n--- ¡RESULTADO! Fallo en la verificación! ---")
        print(f"Motivo: {mensaje_estado}")
        print("Esto puede deberse a un bloqueo del sitio, un cambio en la estructura HTML o un problema de red persistente.")