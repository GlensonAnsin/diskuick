"""Generates assets/diskuick.ico (the exe's file icon) from logo.py."""
import os

from logo import render_logo

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(out, exist_ok=True)
sizes = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]
render_logo(256).save(os.path.join(out, "diskuick.ico"), format="ICO", sizes=[(s, s) for s in sizes])
render_logo(512).save(os.path.join(out, "diskuick.png"))
print("wrote", os.path.join(out, "diskuick.ico"))
