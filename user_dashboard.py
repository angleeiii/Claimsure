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

def _calculate_match_score(lost, found):
    score = _text_match_score(lost["item_name"], found["item_name"]) * 35
    score += _text_match_score(lost["category"], found["category"]) * 20
    if lost["color"] and found["color"]:
        score += _text_match_score(lost["color"], found["color"]) * 15
    score += _text_match_score(lost["location"], found["location"]) * 15
    if lost["date"] and found["date"]:
        try:
            days = abs((lost["date"] - found["date"]).days)
            score += 10 if days == 0 else 7 if days == 1 else 4 if days <= 3 else 0
        except Exception:
            pass
    score += _text_match_score(lost["description"], found["description"]) * 5
    return round(score, 2)
