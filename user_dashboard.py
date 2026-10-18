import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinter import ttk
from database import connect_database
from datetime import datetime
from PIL import Image, ImageTk
import os
import shutil

def _normalize_match_text(value):
    return " ".join(str(value or "").lower().strip().split())
    
def _text_match_score(a, b):
    a = _normalize_match_text(a)
    b = _normalize_match_text(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.8
    aw = set(a.replace(",", " ").split())
    bw = set(b.replace(",", " ").split())
    return len(aw & bw) / max(len(aw), len(bw)) if aw and bw else 0.0
