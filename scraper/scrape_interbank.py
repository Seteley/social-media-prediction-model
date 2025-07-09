from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

def scrape_profile(username: str):
    url = f"https://www.twitterviewer.io/profile/{username}"
    output_file = f"scraper/{username}_raw.txt"
    csv_file = f"data/{username}_raw.csv"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector('h1.text-2xl.md\\:text-3xl.font-bold.tracking-tight')
        html = page.content()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Contenido guardado en {output_file}")
        browser.close()

    # Procesar el HTML y extraer los tweets
    soup = BeautifulSoup(html, "html.parser")
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    tweets = []
    tweet_cards = soup.find_all("div", class_="text-card-foreground")
    for card in tweet_cards:
        # Fecha de publicación
        fecha_pub = ""
        fecha_span = card.find("span", class_="text-slate-500")
        if fecha_span and '·' in fecha_span.text:
            fecha_pub = fecha_span.text.split('·')[-1].strip()
        # Contenido del tweet
        contenido = ""
        contenido_p = card.find("p", class_="text-slate-800")
        if not contenido_p:
            contenido_p = card.find("p", class_="text-slate-800 dark:text-slate-200 whitespace-pre-wrap")
        if contenido_p:
            contenido = contenido_p.text.strip()
        # Números
        nums = card.find_all("span", class_="text-xs")
        respuestas = retweets = likes = guardados = vistas = ""
        if len(nums) >= 5:
            respuestas = nums[0].text.strip()
            retweets = nums[1].text.strip()
            likes = nums[2].text.strip()
            guardados = nums[3].text.strip()
            vistas = nums[4].text.strip()
        tweets.append({
            "timestamp": timestamp,
            "usuario": username,
            "fecha_publicacion": fecha_pub,
            "contenido": contenido,
            "respuestas": respuestas,
            "retweets": retweets,
            "likes": likes,
            "guardados": guardados,
            "vistas": vistas
        })

    # Guardar en CSV
    fieldnames = ["timestamp", "usuario", "fecha_publicacion", "contenido", "respuestas", "retweets", "likes", "guardados", "vistas"]
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "a", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for t in tweets:
            writer.writerow(t)
    print(f"Datos guardados en {csv_file}")

if __name__ == "__main__":
    scrape_profile("interbank")
