from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def check_wcag_compliance(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        return {"error": f"Errore nel recupero della pagina: {e}"}
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    score = 100  
    issues = []

    # 1. Controllo delle immagini senza testo alternativo
    images = soup.find_all('img')
    for img in images:
        if not img.get('alt') or img.get('alt').strip() == "":
            issues.append({
                "type": "Immagine senza testo alternativo",
                "element": str(img),
                "suggestion": "Aggiungere un attributo alt descrittivo"
            })
            score -= 5  

    # 2. Controllo link descrittivi
    links = soup.find_all('a')
    for link in links:
        if link.text.strip().lower() in ["clicca qui", "leggi di più", "scopri di più"]:
            issues.append({
                "type": "Link poco descrittivo",
                "text": link.text.strip(),
                "suggestion": "Utilizzare un testo più chiaro, es. 'Leggi l'articolo completo'"
            })
            score -= 3

    # 3. Controllo intestazioni (H1, H2 senza testo)
    headings = soup.find_all(['h1', 'h2', 'h3'])
    for heading in headings:
        if not heading.text.strip():
            issues.append({
                "type": "Intestazione vuota",
                "element": str(heading),
                "suggestion": "Inserire un testo descrittivo nell'intestazione"
            })
            score -= 5

    # 4. Controllo moduli senza label associati
    forms = soup.find_all('input')
    for form in forms:
        if not form.get('aria-label') and not form.get('label'):
            issues.append({
                "type": "Campo modulo senza etichetta",
                "element": str(form),
                "suggestion": "Aggiungere un'aria-label o una label associata"
            })
            score -= 5

    # 5. Controllo contrasto del testo (approssimativo)
    styles = re.findall(r'color:\s*#([0-9a-fA-F]{6})', html_content)
    backgrounds = re.findall(r'background-color:\s*#([0-9a-fA-F]{6})', html_content)
    for fg, bg in zip(styles, backgrounds):
        if fg.lower() == bg.lower():  
            issues.append({
                "type": "Problema di contrasto",
                "colors": {"text": fg, "background": bg},
                "suggestion": "Migliorare il contrasto tra testo e sfondo"
            })
            score -= 10

    # Classificazione del punteggio
    status = "a rischio" if score < 91 else "conforme"

    return {
        "url": url,
        "score": max(0, score),  
        "status": status,
        "issues": issues
    }

    issues = []

    images = soup.find_all('img')
    for img in images:
        if not img.get('alt') or img.get('alt').strip() == "":
            score -= 5
            issues.append("Immagine senza testo alternativo.")

    links = soup.find_all('a')
    for link in links:
        if link.text.strip().lower() in ["clicca qui", "leggi di più", "scopri di più"]:
            score -= 3
            issues.append("Link poco descrittivo.")

    status = "a rischio" if score < 91 else "conforme"

    return {"url": url, "score": max(0, score), "status": status, "issues": issues}

@app.route('/scan', methods=['GET'])
def scan():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Nessun URL fornito"}), 400
    
    report = check_wcag_compliance(url)
    return jsonify(report)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
