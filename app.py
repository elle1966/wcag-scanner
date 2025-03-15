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
