import re
from urllib.parse import urlparse, quote


def normalizar_telefone(valor: str) -> str:
    """
    Mantém apenas dígitos.

    Por que:
    - Telefones aparecem com espaços, parênteses, hífens, etc.
    - Para montar um link wa.me, precisamos de uma string só com números.
    """
    if not valor:
        return ""
    return re.sub(r"\D", "", str(valor))


def formatar_site(url: str) -> str:
    """
    Normaliza URL do site para um formato consistente.

    Por que:
    - No Google Maps o site pode vir sem http/https ou com redirects.
    - Isso deixa o CSV/Excel mais “limpo” e fácil de clicar/usar.
    """
    if not url:
        return "N/A"

    u = str(url).strip()
    if not u:
        return "N/A"

    if not (u.startswith("http://") or u.startswith("https://")):
        u = "https://" + u

    try:
        p = urlparse(u)
        if not p.netloc:
            return "N/A"
        return f"{p.scheme}://{p.netloc}{p.path}".rstrip("/")
    except Exception:
        return "N/A"


def montar_links_whatsapp(telefone_em_digitos: str, mensagem: str = "") -> tuple[str, str]:
    """
    Gera links do WhatsApp no padrão wa.me.

    Retorno:
    - (link_perfil, link_envio)

    """
    digitos = normalizar_telefone(telefone_em_digitos)
    if not (8 <= len(digitos) <= 15):
        return ("N/A", "N/A")

    base = f"https://wa.me/{digitos}"

    if mensagem:
        texto = quote(mensagem, safe="").replace("%0D%0A", "%0A").replace("%0D", "%0A")
        return (base, f"{base}?text={texto}")

    return (base, base)