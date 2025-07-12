import requests
from bs4 import BeautifulSoup
import time
import os
import boto3

def verificar_talla_especifica(url, talla_a_buscar):
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'DNT': '1'
    }

    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            target_input = soup.find('input', attrs={'data-attr-id': 'size', 'data-attr-value': str(talla_a_buscar)})

            if target_input:
                if 'notify-me-eligible-attribute' in target_input.get('class', []):
                    return False, f"La talla '{talla_a_buscar}' NO está disponible."
                else:
                    return True, f"¡La talla '{talla_a_buscar}' está DISPONIBLE!"
            else:
                return None, f"La talla '{talla_a_buscar}' no fue encontrada."
        except requests.exceptions.RequestException:
            time.sleep(3)
            continue
    return None, "No se pudo verificar la talla."

def lambda_handler(event, context):
    URL_PRODUCTO = "https://www.goldengoose.com/fr/fr/super-star-avec--toile-paillettes-bordeaux-et-contrefort-argent--cod-GWF00102.F004057.11372.html"
    TALLA_A_BUSCAR = "37"
    SNS_TOPIC_ARN = "arn:aws:sns:eu-west-3:907651660072:GoldenCatcher"

    if not SNS_TOPIC_ARN:
        print("ERROR: La variable de entorno SNS_TOPIC_ARN no está configurada.")
        return

    disponible, mensaje = verificar_talla_especifica(URL_PRODUCTO, TALLA_A_BUSCAR)

    if disponible:
        print(f"ÉXITO: Talla encontrada. Enviando notificación a {SNS_TOPIC_ARN}")
        
        asunto_email = f"¡Talla {TALLA_A_BUSCAR} Disponible!"
        cuerpo_email = (
            f"¡Buenas noticias!\n\n"
            f"La talla {TALLA_A_BUSCAR} que buscas ya está disponible.\n\n"
            f"Producto:\n{URL_PRODUCTO}\n\n"
            f"¡Cómprala ahora antes de que se agote!"
        )
        
        try:
            sns_client = boto3.client('sns')
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=cuerpo_email,
                Subject=asunto_email
            )
        except Exception as e:
            print(f"ERROR: No se pudo enviar la notificación a SNS. Causa: {e}")
    else:
        print(f"INFO: Talla no disponible o error en la verificación. No se envía notificación. Motivo: {mensaje}")