import requests
import json
from bs4 import BeautifulSoup

# Función para hacer la petición AJAX y obtener los partidos de una página específica
def obtener_partidos_pagina(pagina):
    url = f'https://www.marathonbet.com/pe/betting/Football?page={pagina}&pageAction=getPage'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Hacemos la solicitud GET
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            # Parseamos la respuesta como JSON
            json_response = json.loads(response.text)
            
            # Extraemos el contenido HTML del campo "content"
            html_content = json_response[0]['content']
            return html_content
        
        except (KeyError, IndexError, json.JSONDecodeError):
            print(f"Error al procesar la respuesta JSON de la página {pagina}")
            return None
    else:
        print(f"Error al obtener los datos de la página {pagina}")
        return None

# Función para obtener los partidos de múltiples páginas
def obtener_datos_marathonbet(paginas):
    partidos = []
    
    for pagina in range(0, paginas + 1):  # Modificar para obtener más páginas
        print(f"Obteniendo datos de la página {pagina}...")
        contenido_html = obtener_partidos_pagina(pagina)
        
        if contenido_html:
            # Parseamos el HTML con BeautifulSoup
            soup = BeautifulSoup(contenido_html, 'html.parser')
            
            # Verificar si se encuentran los eventos de la página
            eventos = soup.find_all('div', class_='coupon-row')
            print(f"Eventos encontrados en la página {pagina}: {len(eventos)}")
            
            for evento in eventos:
                # Obtener nombres de los equipos
                equipo1 = evento.find('div', class_='player1').find('span', {'data-member-link': True}).text.strip()
                equipo2 = evento.find('div', class_='player2').find('span', {'data-member-link': True}).text.strip()
                
                # Obtener las tres primeras cuotas (1X2)
                cuotas = []
                for cuota in evento.find_all('span', class_='selection-link')[:3]:
                    try:
                        cuotas.append(float(cuota['data-selection-price']))
                    except ValueError:
                        continue
                
                # Solo agregamos el partido si tiene exactamente 3 cuotas
                if len(cuotas) == 3:
                    partidos.append({
                        'equipo1': equipo1,
                        'equipo2': equipo2,
                        'cuotas': cuotas
                    })
    
    return partidos

# Función para verificar si existe una surebet y mostrar el resultado del cálculo
def es_surebet(cuotas):
    if len(cuotas) != 3:
        return False, None  # Necesitamos 3 cuotas (ej: 1X2 en fútbol)
    
    # Cálculo del arbitraje: suma de las inversas de las cuotas
    inv_odds = sum(1 / cuota for cuota in cuotas)
    
    # Si la suma de las inversas es menor que 1, tenemos una surebet
    return inv_odds < 1, inv_odds

# Función principal para buscar surebets
def buscar_surebets(url, paginas):
    partidos = obtener_datos_marathonbet(paginas)
    
    for partido in partidos:
        equipo1 = partido['equipo1']
        equipo2 = partido['equipo2']
        cuotas = partido['cuotas']
        
        # Verificamos si es una surebet y mostramos el cálculo del arbitraje
        surebet, inv_odds = es_surebet(cuotas)
        
        if surebet:
            print(f"¡Surebet encontrada entre {equipo1} y {equipo2}! Cuotas: {cuotas}. Resultado del cálculo: {inv_odds:.4f}")
        else:
            print(f"No hay surebet para {equipo1} vs {equipo2}. Cuotas: {cuotas}. Resultado del cálculo: {inv_odds:.4f}")

# URL de Marathonbet (puedes cambiarla por otra sección específica si lo deseas)
url_apuestas = 'https://www.marathonbet.com/pe/betting/Football'

# Ejecutamos el programa para buscar surebets, pasando el número de páginas a consultar
buscar_surebets(url_apuestas, paginas=50)
