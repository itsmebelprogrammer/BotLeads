from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utils import normalizar_telefone, formatar_site, montar_links_whatsapp


@dataclass
class Lead:
    """
    Estrutura simples para “organizar” os dados antes de exportar.

    """
    nome: str
    telefone: str
    site: str
    whatsapp: str
    origem: str = "Google Maps"


def _desembrulhar_redirect_google(href: str) -> str:
    """
    Alguns links do Maps vêm como redirect do Google (google.com/url?...&q=DESTINO).
    Aqui tentamos extrair o destino real.

    Por que:
    - Deixa o 'Site' mais limpo e clicável no arquivo final.
    """
    if not href:
        return ""
    h = href.strip()
    if "google.com/url?" in h and "?q=" in h:
        q = parse_qs(urlparse(h).query).get("q", [""])[0]
        return q or h
    return h


def _texto_seguro(el) -> str:
    """Evita exceção se o Selenium perder o elemento/DOM mudar."""
    try:
        return (el.text or "").strip()
    except Exception:
        return ""


class ColetorGoogleMaps:
    """
    Coletor do Google Maps (somente dados básicos).

     """
    def __init__(self, *, headless: bool = True, pasta_perfil: str = "chrome_profile_temp"):
        self.headless = bool(headless)
        self.pasta_perfil = pasta_perfil
        self.driver = None

    def iniciar(self) -> None:
        """
        Inicia o Chrome via Selenium.

        Motivo desse bloco:
        - O erro 'DevToolsActivePort file doesn't exist' geralmente indica que o Chrome
        caiu ao iniciar, antes de abrir o canal de debug do DevTools.
        - Em headless, alguns ambientes precisam de flags extras para estabilizar.
        - Usar um perfil "fixo" (user-data-dir) pode dar conflito (lock) se sobrar
        chrome.exe aberto, ou se a pasta estiver corrompida/sem permissão.
        """
        import os
        import tempfile
        from pathlib import Path

        options = Options()

        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            # Dica importante: em alguns cenários o pipe é mais estável que porta TCP.
            options.add_argument("--remote-debugging-pipe")  # ajuda no DevToolsActivePort [web:379]
        else:
            options.add_argument("--start-maximized")

        # Flags comuns para reduzir crash no start (inclusive em headless). [web:386]
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # PERFIL TEMPORÁRIO ÚNICO (o ponto mais importante no Windows):
        # - evita conflito/lock de profile
        # - evita reaproveitar pasta corrompida
        # - evita depender de permissão em uma pasta fixa
        pasta_perfil = Path(tempfile.mkdtemp(prefix="maps_profile_"))
        self._pasta_perfil_temp = str(pasta_perfil)  # guardamos para limpar no finalizar()
        options.add_argument(f"--user-data-dir={self._pasta_perfil_temp}")  # pode evitar crash por profile [web:382]

        # Se você quiser, pode fixar idioma pra reduzir variação de layout
        options.add_argument("--lang=pt-BR")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def finalizar(self) -> None:
        """Fecha o driver e tenta remover o perfil temporário criado na inicialização."""
        import shutil

        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

        pasta = getattr(self, "_pasta_perfil_temp", None)
        if pasta:
            try:
                shutil.rmtree(pasta, ignore_errors=True)
            except Exception:
                pass
            self._pasta_perfil_temp = None

    def coletar(self, termo: str, limite: int = 30, *, delay: float = 0.3) -> list[dict]:
        """
        Faz a busca no Maps e coleta até 'limite' resultados.
        """
        if not self.driver:
            raise RuntimeError("Driver não iniciado. Chame iniciar() primeiro.")

        d = self.driver
        w = WebDriverWait(d, 25)

        d.get("https://www.google.com.br/maps")

        # Campo de busca: name="q" costuma ser estável.
        caixa = w.until(EC.element_to_be_clickable((By.NAME, "q")))
        caixa.clear()
        caixa.send_keys(termo)
        caixa.send_keys(Keys.ENTER)

        # Feed de resultados (lado esquerdo) tem role='feed'.
        w.until(EC.presence_of_element_located((By.XPATH, "//div[@role='feed']")))

        leads: list[dict] = []
        vistos = set()

        tentativas_sem_novos = 0

        while len(leads) < limite and tentativas_sem_novos < 8:
            # Cards: a classe hfpxzc é comum nos resultados.
            cards = d.find_elements(By.CLASS_NAME, "hfpxzc")
            if not cards:
                # Fallback para um XPath mais genérico.
                cards = d.find_elements(By.XPATH, "//div[@role='feed']//a[contains(@href,'maps/place')]")

            novos_na_rodada = 0

            for card in cards:
                if len(leads) >= limite:
                    break

                try:
                    d.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
                    card.click()

                    # Nome: DUwDvf normalmente é o h1 do place.
                    nome = ""
                    try:
                        el_nome = w.until(EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf")))
                        nome = _texto_seguro(el_nome)
                    except Exception:
                        pass

                    if not nome:
                        continue
                    if nome in vistos:
                        continue
                    vistos.add(nome)

                    # Site: data-item-id='authority' normalmente é o link de website.
                    site = "N/A"
                    try:
                        a = d.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                        href = _desembrulhar_redirect_google(a.get_attribute("href") or "")
                        # Evita capturar IG/Facebook como "site" (MVP: queremos o site).
                        if href and "instagram.com" not in href.lower() and "facebook." not in href.lower():
                            site = formatar_site(href)
                    except Exception:
                        pass

                    # Telefone: varre Io6YTe e tenta achar algo com cara de telefone.
                    telefone = ""
                    try:
                        w.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Io6YTe")))
                        els = d.find_elements(By.CLASS_NAME, "Io6YTe")
                        for e in els:
                            tx = _texto_seguro(e)
                            dig = normalizar_telefone(tx)
                            if "tel:" in tx.lower() or (dig.isdigit() and len(dig) >= 10):
                                telefone = dig
                                break
                    except Exception:
                        pass

                    link_wpp, _ = montar_links_whatsapp(telefone, "")

                    lead = Lead(
                        nome=nome,
                        telefone=telefone if telefone else "N/A",
                        site=site,
                        whatsapp=link_wpp,
                    )

                    leads.append(
                        {
                            "Nome": lead.nome,
                            "Telefone": lead.telefone,
                            "Site": lead.site,
                            "WhatsApp": lead.whatsapp,
                            "Origem": lead.origem,
                        }
                    )

                    novos_na_rodada += 1

                    # Delay ajuda a reduzir risco de bloqueio e falhas por DOM “correndo”.
                    if delay:
                        time.sleep(delay)

                except Exception:
                    continue

            if novos_na_rodada == 0:
                tentativas_sem_novos += 1
                # Se não apareceu nada novo, rolamos o feed para carregar mais resultados.
                try:
                    feed = d.find_element(By.XPATH, "//div[@role='feed']")
                    d.execute_script("arguments[0].scrollTop += 700;", feed)
                except Exception:
                    pass
                time.sleep(0.6)
            else:
                tentativas_sem_novos = 0

        return leads