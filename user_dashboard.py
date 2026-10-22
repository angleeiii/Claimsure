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

def generate_possible_matches(cursor):
    cursor.execute(
        "SELECT lost_item_id, user_id, item_name, category, description, color, location_lost, date_lost "
        "FROM lost_items WHERE status IN ('ACTIVE','MATCHED')"
    )
    lost_rows = cursor.fetchall()
    cursor.execute(
        "SELECT found_item_id, item_name, category, description, color, location_found, date_found "
        "FROM found_items WHERE status IN ('ACTIVE','MATCHED')"
    )
    found_rows = cursor.fetchall()
    for lost in lost_rows:
        ld = {
            "id": lost[0],
            "user_id": lost[1],
            "item_name": lost[2],
            "category": lost[3],
            "description": lost[4],
            "color": lost[5],
            "location": lost[6],
            "date": lost[7],
        }
        for found in found_rows:
            fd = {
                "id": found[0],
                "item_name": found[1],
                "category": found[2],
                "description": found[3],
                "color": found[4],
                "location": found[5],
                "date": found[6],
            }
            score = _calculate_match_score(ld, fd)
            if score < 40:
                continue
            cursor.execute(
                "SELECT match_id FROM matches WHERE lost_item_id=%s AND found_item_id=%s LIMIT 1",
                (ld["id"], fd["id"]),
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "UPDATE matches SET match_score=%s WHERE match_id=%s AND match_status='POSSIBLE'",
                    (score, existing[0]),
                )
            else:
                cursor.execute(
                    "INSERT INTO matches (lost_item_id, found_item_id, match_score, match_status) "
                    "VALUES (%s, %s, %s, 'POSSIBLE')",
                    (ld["id"], fd["id"], score),
                )
                cursor.execute(
                    "INSERT INTO notifications (user_id, title, message, notification_type) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        ld["user_id"],
                        "Possible Match Found",
                        f"A possible match was found for your lost item: {ld['item_name']}.",
                        "MATCH",
                    ),
                )
