from playwright.sync_api import sync_playwright

def scrape_profile(username: str):
    url = f"https://www.twitterviewer.io/profile/{username}"
    output_file = f"scraper/{username}_raw.txt"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        # Espera hasta que el encabezado del perfil esté visible (contenido real cargado)
        page.wait_for_selector('h1.text-2xl.md\\:text-3xl.font-bold.tracking-tight')
        html = page.content()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Contenido guardado en {output_file}")
        browser.close()

if __name__ == "__main__":
    scrape_profile("cristiano")
