#!/usr/bin/env python3
"""
Deploy do AGREGADOR DE PESQUISAS (electoralpolls.html) para o PythonAnywhere, pela API.

Sobe o electoralpolls.html para /home/<user>/electoralpolls/ e da reload no web app.
Le as credenciais nesta ordem: variaveis de ambiente PA_TOKEN/PA_USER (que e como o
GitHub Actions e a rotina de nuvem passam o segredo) e, se nao houver, o painel/.env
local do Mac. Assim o mesmo arquivo serve nas duas pontas sem token nenhum no repo.

Uso:
  python3 deploy_agregador.py              # valida o JS, sobe e da reload
  python3 deploy_agregador.py --no-reload  # sobe sem reload
  python3 deploy_agregador.py --force      # sobe mesmo se a validacao do JS falhar

Antes de subir, valida a sintaxe do JS embutido (precisa do node). Se o JS estiver
quebrado, ABORTA: melhor nao publicar um painel que nao renderiza.
Somente stdlib.
"""
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE    = Path(__file__).parent
ARQUIVO = BASE / "electoralpolls.html"
# Onde procurar o .env quando NAO ha variavel de ambiente (caso do Mac).
# Caminho ABSOLUTO de proposito: o repositorio nao fica mais ao lado da pasta do painel,
# e a alternativa (symlink "painel" dentro do repo) ja foi tentada em 02/08/2026 e e pior,
# porque o symlink acaba versionado e aponta para fora do repositorio.
def _acha_env():
    """Onde procurar o .env quando NAO ha variavel de ambiente (caso do Mac).

    AGREGADOR_ENV manda, se estiver definida. Senao, procura a pasta do Google
    Drive por padrao em vez de caminho literal: o literal trazia o e-mail do
    dono dentro do nome da pasta, o que nao e segredo mas tambem nao precisa
    ficar num repositorio publico. Varrer tambem sobrevive a trocar de conta.

    Symlink "painel" dentro do repositorio ja foi tentado em 02/08/2026 e e
    pior: acaba versionado e apontando para fora do repositorio.
    """
    manual = os.environ.get("AGREGADOR_ENV")
    if manual:
        return Path(manual)
    raiz = Path.home() / "Library" / "CloudStorage"
    for drive in sorted(raiz.glob("GoogleDrive-*")):
        for conta in sorted(drive.glob("*")):
            alvo = conta / "Brasília - Freire Carvalho" / "Claude" / "painel" / ".env"
            if alvo.exists():
                return alvo
    return raiz / "painel" / ".env"      # inexistente: erra com mensagem clara


ENV     = _acha_env()
REMOTO  = "electoralpolls"                   # /home/<user>/electoralpolls/
API     = "https://www.pythonanywhere.com"


def ler_env():
    """Ambiente primeiro (nuvem/CI), painel/.env depois (Mac). Nunca token no repositorio."""
    cfg = {}
    for k in ("PA_TOKEN", "PA_USER", "PAINEL_URL"):
        v = os.environ.get(k)
        if v:
            cfg[k] = v.strip()
    if cfg.get("PA_TOKEN"):
        return cfg
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    return cfg


def valida_js(path):
    """Roda o mesmo check que usamos a mao: new Function(script) sem erro de sintaxe."""
    m = re.search(r"<script>([\s\S]*)</script>", path.read_text(encoding="utf-8"))
    if not m:
        return False, "nao achei o <script> inline"
    js = m.group(1)
    try:
        p = subprocess.run(
            ["node", "-e", "let s=''; process.stdin.on('data',d=>s+=d).on('end',()=>{"
                           "try{ new Function(s); console.log('OK'); }"
                           "catch(e){ console.log('ERRO: '+e.message); process.exit(2); } });"],
            input=js, text=True, capture_output=True, timeout=60,
        )
    except FileNotFoundError:
        return True, "node nao encontrado; pulei a validacao"
    except subprocess.TimeoutExpired:
        return False, "validacao do JS estourou o tempo"
    out = (p.stdout or p.stderr).strip()
    return p.returncode == 0, out


def upload(user, token, path, nome_remoto):
    """Sobe o conteudo de `path` para /home/<user>/electoralpolls/<nome_remoto>."""
    dest = f"/home/{user}/{REMOTO}/{nome_remoto}"
    url  = f"{API}/api/v0/user/{user}/files/path{dest}"
    data = path.read_bytes()
    boundary = "----pa" + uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="content"; filename="{nome_remoto}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = Request(url, data=body, method="POST", headers={
        "Authorization": f"Token {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    })
    with urlopen(req, timeout=90) as r:
        code = r.getcode()
    return code, dest


def reload_webapp(user, dominio, token):
    url = f"{API}/api/v0/user/{user}/webapps/{dominio}/reload/"
    req = Request(url, data=b"", method="POST",
                  headers={"Authorization": f"Token {token}"})
    with urlopen(req, timeout=60) as r:
        return r.getcode()


def main():
    cfg = ler_env()
    token = cfg.get("PA_TOKEN")
    if not token:
        print("ERRO: falta PA_TOKEN (nem na variavel de ambiente nem em painel/.env)")
        return 1
    user = cfg.get("PA_USER") or cfg.get("PAINEL_URL", "").split("//")[-1].split("/")[0].split(".")[0]
    if not user:
        print("ERRO: nao consegui deduzir o usuario (defina PA_USER)")
        return 1
    dominio = f"{user}.pythonanywhere.com"

    if not ARQUIVO.exists():
        print(f"ERRO: {ARQUIVO.name} nao existe")
        return 1

    ok, msg = valida_js(ARQUIVO)
    print(f"Validacao do JS: {msg}")
    if not ok and "--force" not in sys.argv:
        print("ABORTADO: o JS esta quebrado. Corrija (ou use --force).")
        return 1

    # Sobe o MESMO conteudo com dois nomes, a partir do unico arquivo local:
    #   electoralpolls.html -> URL antiga, que ja estava divulgada
    #   index.html          -> faz a URL limpa /electoralpolls/ funcionar
    # Como os dois saem do mesmo electoralpolls.html local, nao ha como dessincronizar.
    kb = ARQUIVO.stat().st_size / 1024
    for nome in ("electoralpolls.html", "index.html"):
        # 3 tentativas: o PythonAnywhere oscila (timeout/500 durante instabilidade).
        code = dest = None
        for tent in range(1, 4):
            try:
                code, dest = upload(user, token, ARQUIVO, nome)
                break
            except HTTPError as e:
                erro = f"HTTP {e.code}: {e.read().decode(errors='replace')[:120]}"
            except Exception as e:
                erro = f"{type(e).__name__}: {e}"
            if tent < 3:
                print(f"  tentativa {tent} de {nome} falhou ({erro}); repetindo em {tent * 10}s")
                time.sleep(tent * 10)
            else:
                print(f"FALHOU upload de {nome} apos 3 tentativas: {erro}")
                return 1
        print(f"OK {code} ({'criado' if code == 201 else 'atualizado'}): {dest} ({kb:.0f} KB)")

    # O reload so importa para app WSGI (o painel de prazos). Aqui o agregador e ARQUIVO ESTATICO,
    # servido direto pelo mapeamento /electoralpolls/ -> /home/<user>/electoralpolls/. O upload ja
    # basta. Por isso o reload e BEST-EFFORT: se falhar, NAO e erro de deploy.
    # (Em 17/07/2026 o PythonAnywhere caiu; o reload deu 409/timeout e este script chegou a quebrar
    #  com traceback porque socket.timeout nao e URLError. Upload OK != deploy falhou.)
    if "--no-reload" in sys.argv:
        print("Reload pulado (--no-reload).")
    else:
        try:
            rc = reload_webapp(user, dominio, token)
            print(f"Reload OK ({rc}).")
        except Exception as e:
            print(f"Aviso: reload nao concluiu ({type(e).__name__}: {e}).")
            print("       Sem problema: o agregador e estatico, o upload ja vale. Reload so afeta app WSGI.")

    print(f"No ar: https://{dominio}/{REMOTO}/  (e tambem /{REMOTO}/electoralpolls.html)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
