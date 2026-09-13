#!/usr/bin/env python3
"""Render a lamorim.net X/OG card (1200x630) with Fraunces italic title."""
import argparse, html, pathlib, subprocess, tempfile, textwrap

W, H = 1200, 630
FONT_ITALIC = "/usr/share/fonts/truetype/sand-box/google/Fraunces/Fraunces-Italic-VariableFont_SOFT,WONK,opsz,wght.ttf"
FONT_REG = "/usr/share/fonts/truetype/sand-box/google/Fraunces/Fraunces-VariableFont_SOFT,WONK,opsz,wght.ttf"

def wrap_title(title: str, max_chars: int = 22) -> str:
    # soft wrap for big display type
    return "<br>".join(html.escape(line) for line in textwrap.wrap(title, width=max_chars) or [title])

def render(title: str, out: pathlib.Path, site: str = "lamorim.net"):
    title_html = wrap_title(title)
    doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@font-face {{
  font-family: 'Fraunces';
  src: url('file://{FONT_ITALIC}') format('truetype');
  font-style: italic;
  font-weight: 100 900;
}}
@font-face {{
  font-family: 'Fraunces';
  src: url('file://{FONT_REG}') format('truetype');
  font-style: normal;
  font-weight: 100 900;
}}
html, body {{
  margin: 0; padding: 0; width: {W}px; height: {H}px; overflow: hidden;
  background: #f4efe6;
}}
body {{
  position: relative;
  box-sizing: border-box;
  padding: 72px 80px 88px;
  font-family: 'Fraunces', Georgia, serif;
  color: #222;
}}
h1 {{
  margin: 0;
  font-style: italic;
  font-weight: 700;
  font-size: 88px;
  line-height: 1.12;
  font-variation-settings: "SOFT" 100, "WONK" 1, "opsz" 144, "wght" 700;
  max-width: 1040px;
}}
.site {{
  position: absolute;
  right: 80px;
  bottom: 48px;
  font-style: normal;
  font-weight: 500;
  font-size: 28px;
  color: #555;
  font-variation-settings: "SOFT" 0, "WONK" 0, "opsz" 36, "wght" 500;
}}
</style></head>
<body>
  <h1>{title_html}</h1>
  <div class="site">{html.escape(site)}</div>
</body></html>"""
    with tempfile.TemporaryDirectory() as td:
        html_path = pathlib.Path(td) / "card.html"
        html_path.write_text(doc)
        out.parent.mkdir(parents=True, exist_ok=True)
        # Chrome writes to cwd as screenshot.png unless --screenshot=path
        shot = pathlib.Path(td) / "shot.png"
        subprocess.run([
            "google-chrome",
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--screenshot={shot}",
            f"--window-size={W},{H}",
            f"file://{html_path}",
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out.write_bytes(shot.read_bytes())
        print(f"wrote {out} ({out.stat().st_size} bytes)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("title")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()
    render(args.title, pathlib.Path(args.out))
