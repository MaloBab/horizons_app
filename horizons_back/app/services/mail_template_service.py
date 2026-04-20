"""
services/mail_template_service.py

Moteur de template côté serveur :
  - Interpolation des variables {{prenom}}, {{nom}}, {{postes}}, etc.
  - Génération du planning personnel en PDF (pièce jointe) via ReportLab canvas.
    Le rendu est pixel-perfect grâce à un dessin bas niveau reproduisant
    fidèlement le style HTML de référence : fond #0f1623, tableau avec header
    thead, badges pills jour/horaire, chip bénévole cyan, avatar carré arrondi,
    section-title avec point cyan + ligne, méta-badge count.

    ADAPTATION DYNAMIQUE : la hauteur de chaque ligne du tableau s'ajuste
    automatiquement selon le nombre de bénévoles dans la colonne Équipe.
    Les chips s'enroulent sur plusieurs lignes si nécessaire, sans jamais
    tronquer l'équipe.

Le rendu final (body_html interpolé + planning.pdf en PJ) est envoyé
par email_service.send_html_email().
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from io import BytesIO
from typing import Optional

from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.units import mm
from sqlalchemy.orm import Session, joinedload

from .. import models, crud
from ..models.festival import Festival
from ..models.volunteer import Volunteer
from ..models.job import Job


# ── Palette & helpers couleur ─────────────────────────────────────────────────

def _blend(base_hex: str, r: int, g: int, b: int, a: float) -> Color:
    base = HexColor(base_hex)
    br, bg, bb = base.red, base.green, base.blue
    return Color(
        br + (r / 255 - br) * a,
        bg + (g / 255 - bg) * a,
        bb + (b / 255 - bb) * a,
    )


BG              = HexColor("#0f1623")
CYAN            = HexColor("#22d3ee")
CYAN_LIGHT      = HexColor("#67e8f9")
WHITE           = HexColor("#f8fafc")
SLATE_200       = HexColor("#e2e8f0")
SLATE_300       = HexColor("#cbd5e1")
SLATE_400       = HexColor("#94a3b8")
SLATE_500       = HexColor("#64748b")
SLATE_600       = HexColor("#475569")
SLATE_700       = HexColor("#334155")
INDIGO_300      = HexColor("#a5b4fc")
SLATE_100_SOLID = HexColor("#f1f5f9")

TAG_BG          = _blend("#0f1623",   6, 182, 212, 0.12)
TAG_BORDER      = _blend("#0f1623",   6, 182, 212, 0.25)
AVATAR_BG       = _blend("#0f1623",   6, 182, 212, 0.30)
AVATAR_BORDER   = _blend("#0f1623",   6, 182, 212, 0.25)
META_BG         = _blend("#0f1623", 255, 255, 255, 0.05)
META_BORDER     = _blend("#0f1623", 255, 255, 255, 0.08)
HEADER_SEP      = _blend("#0f1623", 255, 255, 255, 0.08)
SECTION_LINE    = _blend("#0f1623", 255, 255, 255, 0.06)
TABLE_BORDER    = _blend("#0f1623", 255, 255, 255, 0.07)
THEAD_BG        = _blend("#0f1623", 255, 255, 255, 0.04)
TH_BORDER       = _blend("#0f1623", 255, 255, 255, 0.07)
ROW_BORDER      = _blend("#0f1623", 255, 255, 255, 0.04)
BADGE_DAY_BG    = _blend("#0f1623",  99, 102, 241, 0.15)
BADGE_DAY_BD    = _blend("#0f1623",  99, 102, 241, 0.20)
BADGE_TIME_BG   = _blend("#0f1623",   6, 182, 212, 0.12)
BADGE_TIME_BD   = _blend("#0f1623",   6, 182, 212, 0.18)
CHIP_SELF_BG    = _blend("#0f1623",   6, 182, 212, 0.14)
CHIP_SELF_BD    = _blend("#0f1623",   6, 182, 212, 0.28)
CHIP_OTHER_BG   = _blend("#0f1623", 255, 255, 255, 0.06)
CHIP_OTHER_BD   = _blend("#0f1623", 255, 255, 255, 0.12)
CHIP_OTHER_FG   = HexColor("#94a3b8")
FOOTER_SEP      = _blend("#0f1623", 255, 255, 255, 0.06)


# ── Helpers texte / slot ──────────────────────────────────────────────────────

DAY_NAMES = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def _format_hour(h: int) -> str:
    return f"{h % 24}h"


def _slot_label(start: int, end: int) -> str:
    return f"de {start}h à {end}h"


def _day_label(day_index: int, festival_start: Optional[date] = None) -> str:
    name = DAY_NAMES[day_index % 7]
    if festival_start is None:
        return name
    real_date = festival_start + timedelta(days=day_index)
    return f"{name} {real_date.day} {real_date.strftime('%B')}"


# ── Primitives de dessin ──────────────────────────────────────────────────────

def _rounded_rect(
    c: rl_canvas.Canvas,
    x: float, y: float, w: float, h: float, r: float,
    fill_color: Color,
    stroke_color: Optional[Color] = None,
    stroke_width: float = 0.5,
) -> None:
    c.saveState()
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_width)
    p = c.beginPath()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.arcTo(x + w - 2 * r, y,            x + w,     y + 2 * r,     startAng=-90, extent=90)
    p.lineTo(x + w, y + h - r)
    p.arcTo(x + w - 2 * r, y + h - 2*r, x + w,     y + h,         startAng=0,   extent=90)
    p.lineTo(x + r, y + h)
    p.arcTo(x,             y + h - 2*r, x + 2 * r, y + h,         startAng=90,  extent=90)
    p.lineTo(x, y + r)
    p.arcTo(x,             y,           x + 2 * r, y + 2 * r,     startAng=180, extent=90)
    p.close()
    c.drawPath(p, fill=1, stroke=1 if stroke_color else 0)
    c.restoreState()


def _pill(
    c: rl_canvas.Canvas,
    x: float,
    y: float,
    text: str,
    font: str,
    font_size: float,
    bg_color: Color,
    border_color: Color,
    fg_color: Color,
    pad_x: float = 9,
    pad_y: float = 3,
) -> float:
    """
    Dessine une pill. Retourne la largeur totale.
    """
    c.setFont(font, font_size)
    tw = c.stringWidth(text, font, font_size)
    pw = tw + pad_x * 2
    ph = font_size + pad_y * 2
    _rounded_rect(c, x, y, pw, ph, ph / 2,
                  fill_color=bg_color, stroke_color=border_color, stroke_width=0.6)
    c.setFillColor(fg_color)
    c.setFont(font, font_size)
    c.drawString(x + pad_x, y + pad_y + 0.8, text)
    return pw


def _pill_width(
    c: rl_canvas.Canvas,
    text: str,
    font: str,
    font_size: float,
    pad_x: float = 9,
) -> float:
    """Calcule la largeur d'une pill sans la dessiner."""
    c.setFont(font, font_size)
    return c.stringWidth(text, font, font_size) + pad_x * 2


def _draw_line(c: rl_canvas.Canvas, x1: float, y: float, x2: float, color: Color,
               width: float = 0.5) -> None:
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y, x2, y)
    c.restoreState()


# ── Calcul layout chips équipe ────────────────────────────────────────────────

CHIP_FONT      = "Helvetica-Bold"
CHIP_FONT_SIZE = 8.0
CHIP_PAD_X     = 8.0
CHIP_PAD_Y     = 3.0
CHIP_GAP_X     = 4.0   # espace horizontal entre chips
CHIP_GAP_Y     = 5.0   # espace vertical entre lignes de chips
CHIP_H         = CHIP_FONT_SIZE + CHIP_PAD_Y * 2   # hauteur d'une chip (~14 pt)
CELL_PAD_X     = 14.0
TD_MIN_H       = 40.0  # hauteur minimale d'une ligne (1 ligne de chips)
CELL_V_PAD     = 8.0   # padding vertical haut+bas dans la cellule


def _layout_chips(
    c: rl_canvas.Canvas,
    teammates: list[str],
    col3_x: float,
    col3_w: float,
) -> list[list[tuple[str, float]]]:
    """
    Calcule le layout des chips sur plusieurs lignes.
    Retourne une liste de lignes, chaque ligne = liste de (nom, largeur_chip).
    """
    available_w = col3_w - CELL_PAD_X  # largeur dispo dans la colonne
    lines: list[list[tuple[str, float]]] = []
    current_line: list[tuple[str, float]] = []
    current_x = 0.0

    for name in teammates:
        w = _pill_width(c, name, CHIP_FONT, CHIP_FONT_SIZE, CHIP_PAD_X)
        # Si la chip ne rentre pas sur la ligne courante, on passe à la ligne suivante
        if current_line and current_x + w > available_w:
            lines.append(current_line)
            current_line = [(name, w)]
            current_x = w + CHIP_GAP_X
        else:
            current_line.append((name, w))
            current_x += w + CHIP_GAP_X

    if current_line:
        lines.append(current_line)

    return lines if lines else [[]]


def _row_height_for_chips(chip_lines: list[list]) -> float:
    """
    Calcule la hauteur de ligne nécessaire pour contenir toutes les lignes de chips.
    """
    n = len(chip_lines)
    if n == 0:
        return TD_MIN_H
    total_chips_h = n * CHIP_H + (n - 1) * CHIP_GAP_Y
    needed = total_chips_h + CELL_V_PAD * 2
    return max(TD_MIN_H, needed)


# ── Génération PDF ────────────────────────────────────────────────────────────

def generate_personal_schedule_pdf(
    volunteer: "Volunteer",
    jobs: list["Job"],
    festival: Optional["Festival"] = None,
    all_volunteers: Optional[list] = None,
    assignments_by_job: Optional[dict] = None,
) -> bytes:
    """
    Génère un PDF du planning personnel.
    La hauteur de chaque ligne s'adapte dynamiquement au nombre de bénévoles
    dans la colonne Équipe : les chips s'enroulent sur plusieurs lignes.
    """
    full_name     = f"{volunteer.first_name} {volunteer.last_name}"
    initials      = f"{volunteer.first_name[0]}{volunteer.last_name[0]}".upper()
    email         = str(volunteer.email)
    count         = len(jobs)
    festival_name = str(festival.name) if festival else "Festival"
    today_str     = date.today().strftime("%d %B %Y")

    vol_name_map: dict[str, str] = {}
    if all_volunteers:
        for v in all_volunteers:
            vol_name_map[str(v.id)] = f"{v.first_name} {v.last_name}"

    sorted_jobs = sorted(jobs, key=lambda j: (j.slot.day_index, j.slot.start_time))
    by_category: dict[str, list] = {}
    for job in sorted_jobs:
        label = job.category.label if job.category else "Affectations"
        by_category.setdefault(label, []).append(job)

    buf = BytesIO()
    W, H = A4
    PAD  = 40.0
    CW   = W - 2 * PAD

    # Largeurs de colonnes
    COL_WIDTHS = [CW * 0.34, CW * 0.16, CW * 0.19, CW * 0.31]
    TH_H       = 34.0
    TH_SIZE    = 8.5
    TD_SIZE    = 10.5

    # Position X de départ de la colonne 3 (Équipe)
    col3_x = PAD + COL_WIDTHS[0] + COL_WIDTHS[1] + COL_WIDTHS[2]
    col3_w = COL_WIDTHS[3]

    c = rl_canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Planning — {full_name}")
    if festival:
        c.setAuthor(festival_name)

    # ── Fond général ──────────────────────────────────────────────────────────
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    y = H - PAD

    # ── Festival tag ──────────────────────────────────────────────────────────
    tag_text  = "Planning bénévole"
    tag_font  = "Helvetica-Bold"
    tag_fsize = 7.5
    c.setFont(tag_font, tag_fsize)
    tag_tw    = c.stringWidth(tag_text, tag_font, tag_fsize)
    dot_r     = 2.5
    dot_gap   = 5
    tag_pad_x = 10
    tag_pad_y = 4
    tag_h     = tag_fsize + tag_pad_y * 2
    dot_area  = dot_r * 2 + dot_gap
    tag_w     = tag_tw + dot_area + tag_pad_x * 2

    tag_y = y - tag_h
    _rounded_rect(c, PAD, tag_y, tag_w, tag_h, tag_h / 2,
                  fill_color=TAG_BG, stroke_color=TAG_BORDER, stroke_width=0.6)
    dot_cx = PAD + tag_pad_x + dot_r
    dot_cy = tag_y + tag_h / 2
    c.setFillColor(CYAN)
    c.circle(dot_cx, dot_cy, dot_r, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.setFont(tag_font, tag_fsize)
    c.drawString(PAD + tag_pad_x + dot_area, tag_y + tag_pad_y + 0.5, tag_text)
    y -= tag_h + 14

    # ── Avatar ────────────────────────────────────────────────────────────────
    av_size = 52
    av_r    = 14
    av_x    = PAD
    av_y    = y - av_size
    _rounded_rect(c, av_x, av_y, av_size, av_size, av_r,
                  fill_color=AVATAR_BG, stroke_color=AVATAR_BORDER, stroke_width=0.8)
    av_font_size = 17
    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", av_font_size)
    iw = c.stringWidth(initials, "Helvetica-Bold", av_font_size)
    c.drawString(av_x + av_size / 2 - iw / 2,
                 av_y + av_size / 2 - av_font_size * 0.35,
                 initials)
    y -= av_size + 14

    # ── Nom ───────────────────────────────────────────────────────────────────
    h1_size = 28
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", h1_size)
    c.drawString(PAD, y - h1_size * 0.75, full_name)
    y -= h1_size + 6

    # ── Subtitle email ────────────────────────────────────────────────────────
    sub_size = 11
    c.setFillColor(SLATE_500)
    c.setFont("Helvetica", sub_size)
    c.drawString(PAD, y - sub_size * 0.75, email)
    y -= sub_size

    # ── Meta-badge coin haut droit ────────────────────────────────────────────
    mb_w, mb_h = 90, 58
    mb_x = W - PAD - mb_w
    mb_y = H - PAD - mb_h
    _rounded_rect(c, mb_x, mb_y, mb_w, mb_h, 10,
                  fill_color=META_BG, stroke_color=META_BORDER, stroke_width=0.6)
    count_str  = str(count)
    count_size = 22
    c.setFillColor(CYAN)
    c.setFont("Helvetica-Bold", count_size)
    cw_str = c.stringWidth(count_str, "Helvetica-Bold", count_size)
    c.drawString(mb_x + mb_w / 2 - cw_str / 2,
                 mb_y + mb_h / 2 + 4,
                 count_str)
    plural   = count > 1
    lbl_text = "POSTES AFFECTÉS" if plural else "POSTE AFFECTÉ"
    lbl_size = 7
    c.setFillColor(SLATE_600)
    c.setFont("Helvetica", lbl_size)
    lw = c.stringWidth(lbl_text, "Helvetica", lbl_size)
    c.drawString(mb_x + mb_w / 2 - lw / 2,
                 mb_y + mb_h / 2 - 18,
                 lbl_text)

    # ── Séparateur header ─────────────────────────────────────────────────────
    y -= 28
    _draw_line(c, PAD, y, W - PAD, HEADER_SEP, width=0.6)
    y -= 40

    # ══════════════════════════════════════════════════════════════════════════
    # SECTIONS + TABLEAUX
    # ══════════════════════════════════════════════════════════════════════════

    def _new_page():
        nonlocal y
        c.showPage()
        c.setFillColor(BG)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(SLATE_700)
        c.setFont("Helvetica", 7.5)
        c.drawString(PAD, H - PAD / 2, full_name)
        c.drawRightString(W - PAD, H - PAD / 2, festival_name)
        _draw_line(c, PAD, H - PAD / 2 - 6, W - PAD, HEADER_SEP, 0.5)
        y = H - PAD - 10

    def _build_teammates(job) -> list[str]:
        """Construit la liste ordonnée des bénévoles pour un poste."""
        job_assignments = (assignments_by_job or {}).get(job.id, [])
        self_id = str(volunteer.id)
        if job_assignments:
            others: list[str] = []
            for assignment in job_assignments:
                v_id = str(assignment.volunteer_id) if hasattr(assignment, "volunteer_id") \
                    else str(assignment.get("volunteer_id", ""))
                if v_id == self_id:
                    continue
                name = vol_name_map.get(v_id)
                if name:
                    others.append(name)
            return [full_name] + others
        return [full_name]

    sections = list(by_category.items())

    for sec_idx, (cat_label, cat_jobs) in enumerate(sections):

        # ── Section title ──────────────────────────────────────────────────────
        sec_margin_top = 32 if sec_idx > 0 else 0
        y -= sec_margin_top

        sec_title_h = 22
        n_rows = len(cat_jobs) if cat_jobs else 1

        # Pré-calcul des layouts chips + hauteurs de ligne pour cette section
        row_chip_layouts: list[list[list[tuple[str, float]]]] = []
        row_heights: list[float] = []
        for job in cat_jobs:
            teammates = _build_teammates(job)
            chip_lines = _layout_chips(c, teammates, col3_x, col3_w)
            row_chip_layouts.append(chip_lines)
            row_heights.append(_row_height_for_chips(chip_lines))

        table_h = TH_H + sum(row_heights)
        needed  = sec_title_h + 14 + table_h + 20

        if y - needed < PAD + 20:
            _new_page()

        # ── Point cyan + titre section ─────────────────────────────────────────
        dot_sec_r = 4
        dot_sec_y = y - sec_title_h / 2
        c.setFillColor(CYAN)
        c.circle(PAD + dot_sec_r, dot_sec_y, dot_sec_r, fill=1, stroke=0)

        sec_text_x = PAD + dot_sec_r * 2 + 10
        c.setFillColor(SLATE_400)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(sec_text_x, dot_sec_y - 3.5, cat_label.upper())

        sec_text_w = c.stringWidth(cat_label.upper(), "Helvetica-Bold", 8)
        line_x = sec_text_x + sec_text_w + 10
        _draw_line(c, line_x, dot_sec_y, W - PAD, SECTION_LINE, 0.6)

        y -= sec_title_h + 14

        # ── Tableau ────────────────────────────────────────────────────────────
        table_top = y
        table_x   = PAD
        table_w   = CW
        full_table_h = TH_H + sum(row_heights)

        # Fond + bordure extérieure
        _rounded_rect(c, table_x, table_top - full_table_h, table_w, full_table_h,
                      12, fill_color=BG, stroke_color=TABLE_BORDER, stroke_width=0.7)

        # ── Thead ──────────────────────────────────────────────────────────────
        thead_y = table_top - TH_H
        _rounded_rect(c, table_x, thead_y, table_w, TH_H, 12,
                      fill_color=THEAD_BG)
        c.setFillColor(THEAD_BG)
        c.rect(table_x, thead_y, table_w, TH_H / 2, fill=1, stroke=0)
        _draw_line(c, table_x, thead_y, table_x + table_w, TH_BORDER, 0.6)

        th_labels = ["POSTE", "JOUR", "HORAIRE", "ÉQUIPE"]
        th_basey  = thead_y + (TH_H - TH_SIZE) / 2 - 1
        col_x     = table_x
        for th_lbl, col_w in zip(th_labels, COL_WIDTHS):
            c.setFillColor(SLATE_600)
            c.setFont("Helvetica-Bold", TH_SIZE)
            c.drawString(col_x + CELL_PAD_X, th_basey, th_lbl)
            col_x += col_w

        # ── Tbody ──────────────────────────────────────────────────────────────
        row_top = table_top - TH_H
        for row_idx, (job, chip_lines, td_h) in enumerate(
                zip(cat_jobs, row_chip_layouts, row_heights)):
            row_bot = row_top - td_h
            is_last = row_idx == n_rows - 1

            if not is_last:
                _draw_line(c, table_x, row_bot, table_x + table_w, ROW_BORDER, 0.5)

            # Baseline verticale centrée pour les éléments sur 1 ligne
            cell_baseline = row_bot + (td_h - TD_SIZE) / 2

            # Col 0 — Nom du poste (centré verticalement)
            c.setFillColor(SLATE_100_SOLID)
            c.setFont("Helvetica-Bold", TD_SIZE)
            job_name = job.name
            max_w    = COL_WIDTHS[0] - CELL_PAD_X * 2
            while c.stringWidth(job_name, "Helvetica-Bold", TD_SIZE) > max_w and len(job_name) > 4:
                job_name = job_name[:-1]
            if job_name != job.name:
                job_name = job_name[:-1] + "…"
            c.drawString(table_x + CELL_PAD_X, cell_baseline, job_name)

            # Col 1 — Badge jour
            day_text = DAY_NAMES[job.slot.day_index % 7]
            bx = table_x + COL_WIDTHS[0] + CELL_PAD_X
            _pill(c, bx, row_bot + (td_h - CHIP_H) / 2,
                  day_text, "Helvetica-Bold", 8,
                  BADGE_DAY_BG, BADGE_DAY_BD, INDIGO_300,
                  pad_x=9, pad_y=3)

            # Col 2 — Badge horaire
            time_text = f"{_format_hour(job.slot.start_time)} – {_format_hour(job.slot.end_time)}"
            bx2 = table_x + COL_WIDTHS[0] + COL_WIDTHS[1] + CELL_PAD_X
            _pill(c, bx2, row_bot + (td_h - CHIP_H) / 2,
                  time_text, "Helvetica-Bold", 8,
                  BADGE_TIME_BG, BADGE_TIME_BD, CYAN_LIGHT,
                  pad_x=9, pad_y=3)

            # ── Col 3 — Chips équipe multi-lignes ─────────────────────────────
            # On commence depuis le haut de la cellule avec padding
            total_chips_h = len(chip_lines) * CHIP_H + (len(chip_lines) - 1) * CHIP_GAP_Y
            # Centrer verticalement le bloc de chips dans la cellule
            chips_block_top = row_top - (td_h - total_chips_h) / 2

            for line_idx, line in enumerate(chip_lines):
                line_y = chips_block_top - line_idx * (CHIP_H + CHIP_GAP_Y) - CHIP_H
                chip_x = col3_x + CELL_PAD_X
                for t_idx, (teammate, chip_w) in enumerate(line):
                    # Le premier élément (index global 0, ligne 0, pos 0) est soi-même
                    is_self = (line_idx == 0 and t_idx == 0)
                    _pill(
                        c, chip_x, line_y,
                        teammate, CHIP_FONT, CHIP_FONT_SIZE,
                        CHIP_SELF_BG  if is_self else CHIP_OTHER_BG,
                        CHIP_SELF_BD  if is_self else CHIP_OTHER_BD,
                        CYAN_LIGHT    if is_self else CHIP_OTHER_FG,
                        pad_x=CHIP_PAD_X, pad_y=CHIP_PAD_Y,
                    )
                    chip_x += chip_w + CHIP_GAP_X

            row_top = row_bot  # avancer au curseur de la prochaine ligne

        y = table_top - full_table_h

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_y = PAD + 20
    _draw_line(c, PAD, footer_y + 14, W - PAD, FOOTER_SEP, 0.5)
    c.setFillColor(SLATE_700)
    c.setFont("Helvetica", 8)
    c.drawString(PAD, footer_y, f"Généré automatiquement · {festival_name}")
    dw = c.stringWidth(today_str, "Helvetica", 8)
    c.drawString(W - PAD - dw, footer_y, today_str)

    c.save()
    return buf.getvalue()


# ── Interpolation des variables ───────────────────────────────────────────────

def _jobs_summary_html(jobs: list) -> str:
    if not jobs:
        return "<em>Aucun poste assigné</em>"
    items = ""
    for job in jobs:
        slot    = job.slot
        day     = _day_label(slot.day_index)
        horaire = _slot_label(slot.start_time, slot.end_time)
        items  += f"<li><strong>{job.name}</strong> — {day}, {horaire}</li>"
    return f"<ul>{items}</ul>"


def _jobs_summary_plain(jobs: list) -> str:
    if not jobs:
        return "Aucun poste assigné"
    lines = []
    for job in jobs:
        slot    = job.slot
        day     = _day_label(slot.day_index)
        horaire = _slot_label(slot.start_time, slot.end_time)
        lines.append(f"• {job.name} — {day}, {horaire}")
    return "\n".join(lines)


VARIABLE_RE = re.compile(r"\{\{(\w+)\}\}")


def interpolate(
    template: str,
    volunteer: "Volunteer",
    jobs: list,
    festival: Optional["Festival"] = None,
) -> str:
    def replace(match: re.Match) -> str:
        key = match.group(1).lower()

        if key == "prenom":
            return str(volunteer.first_name)
        if key == "nom":
            return str(volunteer.last_name)
        if key in ("prenom_nom", "nom_complet"):
            return f"{volunteer.first_name} {volunteer.last_name}"
        if key == "email":
            return str(volunteer.email)
        if key == "telephone":
            return str(volunteer.phone_number)
        if key == "type":
            t = volunteer.volunteer_type
            return t.value if hasattr(t, "value") else str(t)

        if key == "postes":
            return _jobs_summary_html(jobs)
        if key == "postes_texte":
            return _jobs_summary_plain(jobs)
        if key == "nb_postes":
            return str(len(jobs))
        if key == "premier_poste":
            if not jobs:
                return "—"
            j = min(jobs, key=lambda x: (x.slot.day_index, x.slot.start_time))
            return (f"{j.name} ({_day_label(j.slot.day_index)}, "
                    f"{_slot_label(j.slot.start_time, j.slot.end_time)})")
        if key == "dernier_poste":
            if not jobs:
                return "—"
            j = max(jobs, key=lambda x: (x.slot.day_index, x.slot.end_time))
            return (f"{j.name} ({_day_label(j.slot.day_index)}, "
                    f"{_slot_label(j.slot.start_time, j.slot.end_time)})")

        if festival:
            if key == "festival_nom":
                return str(festival.name)
            if key == "festival_edition":
                return str(festival.edition)
            if key in ("festival_lieu", "festival_location"):
                return str(festival.location_name)
            if key == "festival_ville":
                return str(festival.location_city)
            if key == "festival_dates":
                d1 = festival.start_date.strftime("%d/%m/%Y")
                d2 = festival.end_date.strftime("%d/%m/%Y")
                return f"du {d1} au {d2}"

        return match.group(0)

    return VARIABLE_RE.sub(replace, template)


# ── Chargement des données depuis la DB ───────────────────────────────────────

def load_volunteer_with_jobs(
    db: Session,
    volunteer_id,
) -> tuple["Volunteer", list]:
    volunteer = (
        db.query(Volunteer)
        .filter(Volunteer.id == volunteer_id)
        .first()
    )
    if volunteer is None:
        raise ValueError(f"Bénévole {volunteer_id} introuvable")

    assignments = (
        db.query(models.Assignment)
        .options(
            joinedload(models.Assignment.job).joinedload(Job.category),
            joinedload(models.Assignment.job).joinedload(Job.slot),
        )
        .filter(models.Assignment.volunteer_id == volunteer_id)
        .all()
    )

    jobs = [a.job for a in assignments if a.job is not None]
    return volunteer, jobs