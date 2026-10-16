"""Render each slide of the PPTX to PNG via PowerPoint COM for visual QA."""
import os
import sys
import win32com.client

SRC = r"C:\Users\kpssa\.gemini\antigravity\scratch\internship-portal\HireHub_Internship_Portal_Presentation.pptx"
OUT_DIR = r"C:\Users\kpssa\.gemini\antigravity\scratch\internship-portal\docs\presentation\preview"
os.makedirs(OUT_DIR, exist_ok=True)

pp = win32com.client.Dispatch("PowerPoint.Application")
pres = pp.Presentations.Open(SRC, ReadOnly=True, WithWindow=False)
try:
    for i, slide in enumerate(pres.Slides, start=1):
        slide.Export(os.path.join(OUT_DIR, f"slide-{i:02d}.png"), "PNG", 1280, 720)
    print(f"exported {pres.Slides.Count} slides")
finally:
    pres.Close()
    pp.Quit()
