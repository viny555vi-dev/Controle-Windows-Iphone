"""
Controle remoto do PC pelo iPhone (via Wi-Fi, sem instalar app no iPhone).

Instalação (uma vez só):   pip install pynput
Uso:                       python controle_remoto.py
Depois abra no Safari do iPhone o endereço que aparecer no terminal.
PC e iPhone precisam estar na MESMA rede Wi-Fi.
"""
import ctypes
import json
import random
import socket
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def _ativar_dpi():
    """Windows: evita o mouse andar errado em telas com escala de 125%/150%."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


_ativar_dpi()

from pynput.keyboard import Controller as Keyboard
from pynput.keyboard import Key
from pynput.mouse import Button
from pynput.mouse import Controller as Mouse

PORT = 8765
PIN = str(random.randint(1000, 9999))  # evita que outros na rede usem seu PC

mouse = Mouse()
kb = Keyboard()

KEYS = {
    "playpause": Key.media_play_pause, "next": Key.media_next,
    "prev": Key.media_previous, "volup": Key.media_volume_up,
    "voldown": Key.media_volume_down, "mute": Key.media_volume_mute,
    "left": Key.left, "right": Key.right, "up": Key.up, "down": Key.down,
    "space": Key.space, "esc": Key.esc, "enter": Key.enter,
    "backspace": Key.backspace, "tab": Key.tab, "f": "f",
}

HTML = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>Controle</title>
<style>
*{box-sizing:border-box;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent}
html,body{margin:0;height:100%;background:#111;color:#eee;font-family:-apple-system,system-ui,sans-serif;overscroll-behavior:none}
body{display:flex;flex-direction:column;gap:10px;padding:12px;padding-top:max(12px,env(safe-area-inset-top));padding-bottom:max(12px,env(safe-area-inset-bottom))}
#pad{flex:1;background:#1e1e24;border:2px solid #333;border-radius:18px;display:flex;align-items:center;justify-content:center;color:#666;text-align:center;font-size:14px;touch-action:none}
.row{display:grid;gap:8px}
.r3{grid-template-columns:repeat(3,1fr)}.r4{grid-template-columns:repeat(4,1fr)}
button{background:#2b2b34;color:#eee;border:0;border-radius:12px;padding:14px 0;font-size:16px}
button:active{background:#4a4af0}
#txt{width:100%;padding:12px;border-radius:12px;border:0;background:#2b2b34;color:#eee;font-size:16px;-webkit-user-select:text;user-select:text}
</style></head><body>
<div id="pad">Touchpad<br>1 dedo: mover · toque: clique<br>2 dedos: rolar · toque com 2: botão direito</div>
<div class="row r3">
  <button data-c="click">Clique</button><button data-c="rclick">Direito</button><button data-k="f">Tela cheia</button>
</div>
<div class="row r4">
  <button data-k="prev">⏮</button><button data-k="playpause">⏯</button><button data-k="next">⏭</button><button data-k="mute">🔇</button>
</div>
<div class="row r4">
  <button data-k="voldown">Vol −</button><button data-k="volup">Vol +</button><button data-k="left">◀ 10s</button><button data-k="right">10s ▶</button>
</div>
<div class="row r4">
  <button data-k="space">Espaço</button><button data-k="esc">Esc</button><button data-k="enter">Enter</button><button data-k="backspace">⌫</button>
</div>
<input id="txt" placeholder="Digitar texto e tocar em Enviar…" autocomplete="off" autocapitalize="off">
<script>
const pin = new URLSearchParams(location.search).get('pin') || '';
function send(o){ fetch('/cmd',{method:'POST',body:JSON.stringify({pin,...o}),keepalive:true}).catch(()=>{}); }

let dx=0, dy=0, sc=0;
setInterval(()=>{
  const ix=Math.trunc(dx), iy=Math.trunc(dy);
  if(ix||iy){ send({t:'move',dx:ix,dy:iy}); dx-=ix; dy-=iy; }
  const s=Math.trunc(sc/12);
  if(s){ send({t:'scroll',dy:s}); sc-=s*12; }
}, 16);

const pad=document.getElementById('pad');
let last=null, start=0, moved=0, maxT=0;
const pos=e=>{let x=0,y=0;for(const t of e.touches){x+=t.clientX;y+=t.clientY}return{x:x/e.touches.length,y:y/e.touches.length}};

pad.addEventListener('touchstart',e=>{
  e.preventDefault();
  if(maxT===0){ start=Date.now(); moved=0; }
  maxT=Math.max(maxT,e.touches.length);
  last=pos(e);
},{passive:false});

pad.addEventListener('touchmove',e=>{
  e.preventDefault();
  const p=pos(e), ddx=p.x-last.x, ddy=p.y-last.y;
  moved+=Math.abs(ddx)+Math.abs(ddy);
  if(e.touches.length===1){ dx+=ddx*1.8; dy+=ddy*1.8; } else { sc+=ddy; }
  last=p;
},{passive:false});

pad.addEventListener('touchend',e=>{
  e.preventDefault();
  if(e.touches.length===0){
    if(Date.now()-start<250 && moved<10) send({t: maxT>=2 ? 'rclick' : 'click'});
    maxT=0;
  } else last=pos(e);
},{passive:false});

document.querySelectorAll('button[data-k]').forEach(b=>b.onclick=()=>send({t:'key',k:b.dataset.k}));
document.querySelectorAll('button[data-c]').forEach(b=>b.onclick=()=>send({t:b.dataset.c}));
const txt=document.getElementById('txt');
txt.addEventListener('keydown',e=>{ if(e.key==='Enter'){ send({t:'text',s:txt.value}); txt.value=''; } });
</script></body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silencia o log
        pass

    def do_GET(self):
        body = HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            d = json.loads(self.rfile.read(n))
        except Exception:
            d = {}
        ok = d.get("pin") == PIN
        if ok:
            try:
                t = d.get("t")
                if t == "move":
                    mouse.move(int(d["dx"]), int(d["dy"]))
                elif t == "click":
                    mouse.click(Button.left)
                elif t == "rclick":
                    mouse.click(Button.right)
                elif t == "scroll":
                    mouse.scroll(0, int(d["dy"]))
                elif t == "key" and d.get("k") in KEYS:
                    kb.tap(KEYS[d["k"]])
                elif t == "text":
                    kb.type(str(d.get("s", "")))
            except Exception:
                pass
        self.send_response(200 if ok else 403)
        self.send_header("Content-Length", "0")
        self.end_headers()


def ips_locais():
    ips = []
    try:
        sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sk.connect(("10.255.255.255", 1))  # não envia nada, só descobre a rede ativa
        ips.append(sk.getsockname()[0])
        sk.close()
    except Exception:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith("127.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    return ips or ["IP-DO-SEU-PC"]


def autoteste():
    """Usado pelo GitHub para verificar se o executavel realmente funciona."""
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    html = urllib.request.urlopen(base + "/").read().decode("utf-8")
    assert "Touchpad" in html, "pagina nao carregou"
    corpo = json.dumps({"pin": PIN, "t": "move", "dx": 0, "dy": 0}).encode()
    resp = urllib.request.urlopen(urllib.request.Request(base + "/cmd", data=corpo, method="POST"))
    assert resp.status == 200, "comando nao aceito"
    srv.shutdown()
    print("TESTE OK")


def pausar():
    if getattr(sys, "frozen", False):  # só no .exe: mantém a janela aberta para ler a mensagem
        input("\nPressione Enter para fechar...")


def main():
    if "--teste" in sys.argv:
        autoteste()
        return
    try:
        servidor = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    except OSError:
        print(f"Erro: a porta {PORT} já está em uso. O programa talvez já esteja aberto.")
        pausar()
        return

    print("\n=== Controle remoto ativo ===")
    print("No Safari do iPhone (mesmo Wi-Fi do PC), abra:\n")
    for ip in ips_locais():
        print(f"   http://{ip}:{PORT}/?pin={PIN}")
    print("\nSe não abrir, teste o outro endereço (se houver) e permita o programa no Firewall.")
    print("Dica: no Safari, Compartilhar > 'Adicionar à Tela de Início'.")
    print("Para parar: feche esta janela.\n")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        pausar()
        sys.exit(1)
