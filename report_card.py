#!/usr/bin/env python3
"""
Batch Report Card Generator  (Navy / Yellow "Homeschool" Theme)
Connects 8 Class CSVs → individual PDF report cards (Macro Vision Academy)

Usage:
    python report_card_generator.py                          # demo: top student per class
    python report_card_generator.py --all                    # all 3200 students
    python report_card_generator.py --id S020167             # single student by ID
    python report_card_generator.py --class Class_10 --n 5  # first 5 from one class
"""

import os, sys, argparse, zipfile
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor, white, black
from io import BytesIO

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
CSV_DIR    = "/mnt/user-data/uploads"
OUTPUT_DIR = "/mnt/user-data/outputs/report_cards"
SCHOOL     = "Macro Vision Academy"
TAGLINE    = "Building Future Leaders"
YEAR       = "2025-2026"

# Optional school logo (PNG/JPG). If the file exists it is drawn in the
# top-right badge; otherwise a plain placeholder badge is drawn instead.
LOGO_PATH  = "photo/newlogo.png"

# Maps each CSV file key → its subject mark columns (in display order)
SUBJECT_COLS = {
    "Class_9": [
        "Maths_Marks", "Science_Marks", "English_Marks",
        "SocialScience_Marks", "Computer_Marks", "Hindi_Marks",
    ],
    "Class_10": [
        "Maths_Marks", "Science_Marks", "English_Marks",
        "SocialScience_Marks", "Computer_Marks", "Hindi_Marks",
    ],
    "Class_11_PCM": [
        "Maths_Marks", "Physics_Marks", "Chemistry_Marks",
        "English_Marks", "Physical_eduction_Marks", "Hindi_Marks",
    ],
    "Class_11_PCB": [
        "Biology_Marks", "Physics_Marks", "Chemistry_Marks",
        "English_Marks", "Physical_education_Marks", "Hindi_Marks",
    ],
    "Class_11_Commerce": [
        "Business_Marks", "Accountancy_Marks", "Economics_Marks",
        "English_Marks", "Physical_education_Marks", "Hindi_Marks",
    ],
    "Class_12_PCM": [
        "Maths_Marks", "Physics_Marks", "Chemistry_Marks",
        "English_Marks", "Physical_eduction_Marks_Marks", "Hindi_Marks",
    ],
    "Class_12_PCB": [
        "Biology_Marks", "Physics_Marks", "Chemistry_Marks",
        "English_Marks", "Physical_education_Marks", "Hindi_Marks",
    ],
    "Class_12_Commerce": [
        "Business_Marks", "Accountancy_Marks", "Economics_Marks",
        "English_Marks", "Physical_education_Marks", "Hindi_Marks",
    ],
}

CSV_FILES = {
    "Class_9":           "Class_9.csv",
    "Class_10":          "Class_10.csv",
    "Class_11_PCM":      "Class_11_PCM.csv",
    "Class_11_PCB":      "Class_11_PCB.csv",
    "Class_11_Commerce": "Class_11_Commerce.csv",
    "Class_12_PCM":      "Class_12_PCM.csv",
    "Class_12_PCB":      "Class_12_PCB.csv",
    "Class_12_Commerce": "Class_12_Commerce.csv",
}

# Human-readable subject labels
LABEL_MAP = {
    "Maths_Marks":                 "Mathematics",
    "Science_Marks":               "Science",
    "English_Marks":               "English",
    "SocialScience_Marks":         "Social Science",
    "Computer_Marks":              "Computer Science",
    "Hindi_Marks":                 "Hindi",
    "Physics_Marks":               "Physics",
    "Chemistry_Marks":             "Chemistry",
    "Biology_Marks":               "Biology",
    "Physical_education_Marks":    "Physical Education",
    "Physical_eduction_Marks":     "Physical Education",
    "Physical_eduction_Marks_Marks":"Physical Education",
    "Business_Marks":              "Business Studies",
    "Accountancy_Marks":           "Accountancy",
    "Economics_Marks":             "Economics",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def marks_to_grade(marks: float) -> str:
    """CBSE grading scale."""
    if marks >= 91: return "A1"
    if marks >= 81: return "A2"
    if marks >= 71: return "B1"
    if marks >= 61: return "B2"
    if marks >= 51: return "C1"
    if marks >= 41: return "C2"
    if marks >= 33: return "D"
    return "F"

def generate_remark(row: pd.Series) -> str:
    name  = str(row.get("Student_Name", "Student")).split()[0]
    pct   = float(row.get("Percentage", 0))
    att   = float(row.get("Attendance_Percentage", 0))
    lf    = str(row.get("Least_Favorite_Subject", ""))

    if pct >= 90:
        perf = f"{name} has delivered an outstanding academic performance this year."
    elif pct >= 75:
        perf = f"{name} has shown commendable progress and consistent performance."
    elif pct >= 60:
        perf = f"{name} has performed satisfactorily and shows potential for improvement."
    else:
        perf = f"{name} needs to put in more effort to improve academic results."

    att_note = (
        "Attendance has been excellent." if att >= 90 else
        "Attendance has been good." if att >= 75 else
        "Attendance needs significant improvement."
    )

    focus = (f" Focus on strengthening {lf.replace('_',' ')}."
             if (lf and lf.lower() not in ("nan","")) else "")

    return f"{perf} {att_note}{focus}"


def row_to_student_data(row: pd.Series, subject_cols: list) -> dict:
    """Convert one CSV row → student_data dict for create_report_card()."""
    subjects = []
    for col in row.index:

        if col.endswith("_Marks") and pd.notna(row[col]):

            try:
                m = int(float(row[col]))

                subjects.append({
                    "name": LABEL_MAP.get(
                        col,
                        col.replace("_Marks", "").replace("_", " ")
                    ),
                    "marks": str(m),
                    "grade": marks_to_grade(m),
                })

            except:
                pass

    pct  = float(row.get("Percentage", 0))
    career = str(row.get("Career_Goal", ""))

    return {
        "name":         str(row.get("Student_Name", "")),
        "student_id":   str(row.get("Student_ID", "")),
        "class":        str(row.get("Class", "")),
        "section":      str(row.get("Section", "")),
        "gender":       str(row.get("Gender", "")),
        "student_type": str(row.get("Student_Type", "")),
        "school_year":  YEAR,
        "school_name":  SCHOOL,
        "subjects":     subjects,
        "total_marks":  str(int(float(row.get("Total_Marks", 0)))),
        "percentage":   f"{pct:.2f}%",
        "overall_grade":marks_to_grade(pct),
        "rank":         str(int(float(row.get("Rank", 0)))),
        "attendance":   f"{float(row.get('Attendance_Percentage', 0)):.1f}%",
        "career_goal":  career if career.lower() not in ("nan","") else "",
        "comments":     generate_remark(row),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATOR  —  Navy / Yellow "Homeschool" Theme
# ─────────────────────────────────────────────────────────────────────────────

def create_report_card(sd: dict, output_path: str = None) -> BytesIO:
    """
    Render one student's report card as a PDF.
    sd = student_data dict from row_to_student_data().
    Returns BytesIO; also writes to output_path if given.
    """
    buf = BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=letter)
    W, H = letter   # 612 × 792

    # ── palette (matches the navy / yellow / powder-blue reference design) ──
    NAVY   = HexColor("#122C46")
    NAVY2  = HexColor("#0D2036")   # slightly darker, used for shadows/lines
    YELLOW = HexColor("#F6C445")
    LBLUE  = HexColor("#9EC9D6")
    WHITEC = white
    M      = 40
    CW     = W - 2 * M

    # ── tiny helpers ─────────────────────────────────────────────────────────
    def rbox(x, y, w, h, fill, radius=5, stroke=None, lw=1):
        c.setFillColor(fill)
        if stroke:
            c.setStrokeColor(stroke); c.setLineWidth(lw)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)

    def box(x, y, w, h, fill=LBLUE, stroke=YELLOW, lw=1):
        c.setFillColor(fill); c.setStrokeColor(stroke)
        c.setLineWidth(lw); c.rect(x, y, w, h, fill=1, stroke=1)

    def wrap(text, x, y, max_w, font="Helvetica", sz=9, lead=12, color=NAVY):
        c.setFont(font, sz); c.setFillColor(color)
        line = ""
        for word in str(text).split():
            probe = f"{line} {word}".strip()
            if c.stringWidth(probe, font, sz) <= max_w:
                line = probe
            else:
                c.drawString(x, y, line); y -= lead; line = word
        if line: c.drawString(x, y, line)
        return y

    def zigzag(x, y, length, amplitude=5, segments=10, color=YELLOW, lw=2.2):
        """Small decorative wave, like the ribbon accents in the reference art."""
        c.setStrokeColor(color); c.setLineWidth(lw)
        step = length / segments
        pts = []
        for i in range(segments + 1):
            px = x + i * step
            py = y + (amplitude if i % 2 == 0 else -amplitude)
            pts.append((px, py))
        for i in range(len(pts) - 1):
            c.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])

    def corner_rings(cx, cy, base_color=YELLOW):
        """Nested circle / ring flourish used in the two page corners."""
        c.setFillColor(base_color)
        c.circle(cx, cy, 62, fill=1, stroke=0)
        c.setStrokeColor(base_color); c.setLineWidth(6)
        c.circle(cx + 14, cy - 30, 92, fill=0, stroke=1)
        c.setStrokeColor(base_color); c.setLineWidth(4)
        c.circle(cx - 10, cy + 40, 40, fill=0, stroke=1)

    # ════════════════════════════════════════════════════════════
    # 0. BACKGROUND + DECORATIVE FLOURISHES
    # ════════════════════════════════════════════════════════════
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    corner_rings(-10, H - 5)                 # top-left
    corner_rings(W + 5, 55, base_color=YELLOW)  # bottom-right

    zigzag(0, 70, 130, amplitude=6, segments=10)
    zigzag(0, 45, 130, amplitude=6, segments=10)

    # ════════════════════════════════════════════════════════════
    # 1. HEADER — title + tagline + school badge
    # ════════════════════════════════════════════════════════════
    c.setFillColor(YELLOW)
    c.setFont("Helvetica-Bold", 30)
    title_y = H - 70
    c.drawString(M + 60, title_y, "REPORT CARD")
    tw = c.stringWidth("REPORT CARD", "Helvetica-Bold", 30)
    c.setStrokeColor(YELLOW); c.setLineWidth(2)
    c.line(M + 60, title_y - 6, M + 60 + tw, title_y - 6)

    c.setFont("Helvetica-Bold", 13)
    c.drawString(M + 60, title_y - 32, TAGLINE)

    # school badge (top-right) — uses LOGO_PATH image if present
    BW, BH = 190, 60
    bx, by = W - M - BW, H - BH - 14
    rbox(bx, by, BW, BH, fill=WHITEC, radius=6, stroke=YELLOW, lw=1.5)
    if os.path.exists(LOGO_PATH):
        try:
            c.drawImage(LOGO_PATH, bx + 6, by + 6, width=BW - 12, height=BH - 12,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    else:
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 12)
        words = sd.get("school_name", SCHOOL).split()
        c.drawCentredString(bx + BW/2, by + BH/2 + 10, words[0] if words else SCHOOL)
        c.setFont("Helvetica", 9)
        c.drawCentredString(bx + BW/2, by + BH/2 - 6, " ".join(words[1:]))

    y = H - 150

    # ════════════════════════════════════════════════════════════
    # 2. STUDENT INFORMATION — yellow label boxes (row A + row B)
    # ════════════════════════════════════════════════════════════
    def info_box(x, w, label, value, h=42):
        rbox(x, y - h, w, h, fill=YELLOW, radius=4)
        c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 12, y - 17, label)
        c.setFont("Helvetica", 10)
        c.drawString(x + 12, y - 33, str(value) if value else "—")

    GAP = 14
    wa = [(CW - 2*GAP) * 0.40, (CW - 2*GAP) * 0.30, (CW - 2*GAP) * 0.30]
    xa = [M, M + wa[0] + GAP, M + wa[0] + wa[1] + 2*GAP]
    for x, w, lbl, v in zip(xa, wa,
                             ["Student Name:", "Class:", "Section:"],
                             [sd["name"], sd["class"], sd["section"]]):
        info_box(x, w, lbl, v)
    y -= 42 + 16

    wb = [(CW - GAP) * 0.5, (CW - GAP) * 0.5]
    xb = [M, M + wb[0] + GAP]
    for x, w, lbl, v in zip(xb, wb,
                             ["Student ID / Academic Year:", "Gender / Student Type:"],
                             [f"{sd['student_id']}   ·   {sd['school_year']}",
                              f"{sd['gender']}   ·   {sd['student_type']}"]):
        info_box(x, w, lbl, v)
    y -= 42 + 26

    # ════════════════════════════════════════════════════════════
    # 3. MARKS TABLE — yellow header, powder-blue body w/ yellow gridlines
    # ════════════════════════════════════════════════════════════
    TW = [CW*0.52, CW*0.24, CW*0.24]
    TX = [M, M+TW[0], M+TW[0]+TW[1]]
    RH = 22
    HEAD_H = 26

    rbox(M, y - HEAD_H, CW, HEAD_H, fill=YELLOW, radius=4)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 10)
    for h, x in zip(["School Subject", "Marks (Out of 100)", "Grade"], TX):
        c.drawString(x + 10, y - HEAD_H + 9, h)
    y -= HEAD_H

    n_rows   = max(len(sd.get("subjects", [])), 1)
    body_top = y
    body_h   = RH * n_rows
    box(M, body_top - body_h, CW, body_h, fill=LBLUE, stroke=YELLOW, lw=1.4)
    # vertical gridlines separating the three columns
    c.setStrokeColor(YELLOW); c.setLineWidth(1.2)
    for x in [TX[1], TX[2]]:
        c.line(x, body_top - body_h, x, body_top)

    ry = body_top
    for subj in sd.get("subjects", []):
        ry -= RH
        c.setStrokeColor(YELLOW); c.setLineWidth(0.6)
        c.line(M, ry, M + CW, ry)
        c.setFillColor(NAVY); c.setFont("Helvetica", 10)
        for v, x in zip([subj["name"], subj["marks"], subj["grade"]], TX):
            c.drawString(x + 10, ry + 7, str(v))
    y = body_top - body_h - 14

    # totals bar
    TOT_H = 26
    rbox(M, y - TOT_H, CW, TOT_H, fill=YELLOW, radius=4)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 10)
    c.drawString(M + 10, y - TOT_H + 9,
                 f"Total Marks: {sd['total_marks']}   |   Percentage: {sd['percentage']}")
    c.drawString(TX[2] + 10, y - TOT_H + 9, f"Overall: {sd['overall_grade']}")
    y -= TOT_H + 22

    # ════════════════════════════════════════════════════════════
    # 4. GRADING CONVERSIONS  (left)   +   STUDENT PROFILE (right)
    # ════════════════════════════════════════════════════════════
    LEFT_W  = CW * 0.58
    RIGHT_W = CW - LEFT_W - 18
    right_x = M + LEFT_W + 18

    section_top = y
    HEAD_H2 = 22

    # -- left: grading conversions --
    rbox(M, section_top - HEAD_H2, LEFT_W, HEAD_H2, fill=YELLOW, radius=4)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 10)
    c.drawString(M + 10, section_top - HEAD_H2 + 7, "GRADING CONVERSIONS (CBSE)")

    grading = [
        "A1: 91-100", "A2: 81-90", "B1: 71-80", "B2: 61-70",
        "C1: 51-60", "C2: 41-50", "D: 33-40",  "F: Below 33",
    ]
    rows_needed = 4
    body_h2 = rows_needed * 16 + 14
    box(M, section_top - HEAD_H2 - body_h2, LEFT_W, body_h2, fill=LBLUE, stroke=YELLOW, lw=1.2)
    col1 = grading[:4]; col2 = grading[4:]
    gy = section_top - HEAD_H2 - 16
    c.setFillColor(NAVY); c.setFont("Helvetica", 9)
    for item in col1:
        c.drawString(M + 12, gy, f"\u2022  {item}"); gy -= 16
    gy = section_top - HEAD_H2 - 16
    for item in col2:
        c.drawString(M + LEFT_W/2 + 6, gy, f"\u2022  {item}"); gy -= 16

    left_bottom = section_top - HEAD_H2 - body_h2

    # -- right: student profile, styled like stacked "term" chips --
    profile = [f"Attendance: {sd['attendance']}", f"Class Rank: #{sd['rank']}"]
    if sd.get("career_goal"):
        # keep long career-goal text from overflowing the chip width
        goal = sd["career_goal"]
        max_chars = 34
        if len(goal) > max_chars:
            goal = goal[:max_chars - 1].rstrip() + "…"
        profile.append(f"Career Goal: {goal}")

    chip_h    = 22
    chip_gap  = 7
    TITLE_H   = 28
    PAD_BOT   = 10
    outer_h   = TITLE_H + len(profile) * (chip_h + chip_gap) - chip_gap + PAD_BOT

    c.setStrokeColor(YELLOW); c.setLineWidth(1.4)
    c.roundRect(right_x, section_top - outer_h, RIGHT_W, outer_h, 5, fill=0, stroke=1)

    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 9)
    c.drawString(right_x + 10, section_top - 16, "Student Profile")

    cy = section_top - TITLE_H
    for item in profile:
        rbox(right_x + 8, cy - chip_h, RIGHT_W - 16, chip_h, fill=YELLOW, radius=4)
        c.setFillColor(NAVY); c.setFont("Helvetica", 9)
        c.drawString(right_x + 16, cy - chip_h + 7, item)
        cy -= chip_h + chip_gap

    right_bottom = section_top - outer_h
    y = min(left_bottom, right_bottom) - 22

    # ════════════════════════════════════════════════════════════
    # 5. REMARKS
    # ════════════════════════════════════════════════════════════
    RM_HEAD = 22
    rbox(M, y - RM_HEAD, CW, RM_HEAD, fill=YELLOW, radius=4)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 10)
    c.drawString(M + 10, y - RM_HEAD + 7, "REMARKS")
    y -= RM_HEAD

    CMT_H = 56
    box(M, y - CMT_H, CW, CMT_H, fill=LBLUE, stroke=YELLOW, lw=1.2)
    wrap(sd.get("comments", ""), M + 10, y - 16, CW - 20, color=NAVY)
    y -= CMT_H + 24

    # ════════════════════════════════════════════════════════════
    # 6. SIGNATURES
    # ════════════════════════════════════════════════════════════
    SW = CW / 3
    for i, lbl in enumerate(["Parent's Signature:", "Class Teacher:", "Principal:"]):
        sx = M + i * SW
        c.setFillColor(YELLOW); c.setFont("Helvetica-Bold", 9)
        c.drawString(sx + 5, y, lbl)
        c.setStrokeColor(YELLOW); c.setLineWidth(1)
        c.line(sx + 5, y - 26, sx + SW - 12, y - 26)
        c.setFillColor(LBLUE); c.setFont("Helvetica", 8)
        c.drawString(sx + 5, y - 38, "(Signature & Stamp)")

    # ════════════════════════════════════════════════════════════
    # 7. FOOTER
    # ════════════════════════════════════════════════════════════
    c.setFillColor(YELLOW)
    c.rect(0, 0, W, 26, fill=1, stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W/2, 9,
        f"{SCHOOL}  \u2022  Academic Year {YEAR}  "
        f"\u2022  Student ID: {sd['student_id']}  \u2022  Official Report Card")

    c.save(); buf.seek(0)
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(buf.read())
        buf.seek(0)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# BATCH RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def load_all_csvs(csv_dir: str = CSV_DIR) -> dict:
    """Load all 8 CSVs; returns {class_key: DataFrame}."""
    dfs = {}
    for key, fname in CSV_FILES.items():
        path = os.path.join(csv_dir, fname)
        if os.path.exists(path):
            dfs[key] = pd.read_csv(path)
        else:
            print(f"  [WARN] {fname} not found in {csv_dir}")
    return dfs


def find_student(student_id: str, dfs: dict) -> tuple:
    """Return (class_key, row) for a given Student_ID across all CSVs."""
    for key, df in dfs.items():
        match = df[df["Student_ID"] == student_id]
        if not match.empty:
            return key, match.iloc[0]
    return None, None


def generate_batch(
    csv_dir:    str  = CSV_DIR,
    output_dir: str  = OUTPUT_DIR,
    n_per_class: int = None,   # None = all students
) -> int:
    """
    Generate PDFs for every student (or first n_per_class students per CSV).
    Files are saved as:  output_dir/<class_key>/<Student_ID>.pdf
    Returns total count generated.
    """
    dfs   = load_all_csvs(csv_dir)
    total = 0
    for key, df in dfs.items():
        subset = df if n_per_class is None else df.head(n_per_class)
        cols   = SUBJECT_COLS[key]
        for _, row in subset.iterrows():
            sd   = row_to_student_data(row, cols)
            path = os.path.join(output_dir, key, f"{sd['student_id']}.pdf")
            create_report_card(sd, path)
            total += 1
        print(f"  ✓  {key}: {len(subset)} PDFs")
    print(f"\n  Total: {total} report cards → {output_dir}")
    return total


def generate_demo(
    csv_dir:    str = CSV_DIR,
    output_dir: str = OUTPUT_DIR,
) -> list:
    """
    Generate one sample PDF per class (rank #1 student).
    Returns list of created file paths.
    """
    dfs   = load_all_csvs(csv_dir)
    paths = []
    for key, df in dfs.items():
        top = df[df["Rank"] == 1].iloc[0] if 1 in df["Rank"].values else df.iloc[0]
        sd  = row_to_student_data(top, SUBJECT_COLS[key])
        out = os.path.join(output_dir, "demo", f"{key}_sample.pdf")
        create_report_card(sd, out)
        paths.append(out)
        print(f"  ✓  {key}  →  {sd['name']}")
    return paths


# ─────────────────────────────────────────────────────────────────────────────
# CLI  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Report Card Generator")
    parser.add_argument("--all",   action="store_true", help="Generate all ~3200 PDFs")
    parser.add_argument("--demo",  action="store_true", help="One sample PDF per class (default)")
    parser.add_argument("--id",    type=str,            help="Generate for a single Student_ID")
    parser.add_argument("--class", dest="cls", type=str,help="Class key (e.g. Class_10)")
    parser.add_argument("--n",     type=int, default=5, help="Number of students when using --class")
    parser.add_argument("--csv",   type=str, default=CSV_DIR,    help="Directory containing CSVs")
    parser.add_argument("--out",   type=str, default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    if args.id:
        dfs = load_all_csvs(args.csv)
        key, row = find_student(args.id, dfs)
        if row is None:
            print(f"Student {args.id} not found.")
            sys.exit(1)
        sd   = row_to_student_data(row, SUBJECT_COLS[key])
        path = os.path.join(args.out, f"{args.id}.pdf")
        create_report_card(sd, path)
        print(f"✅  {path}")

    elif args.cls:
        if args.cls not in CSV_FILES:
            print(f"Unknown class key. Choose from: {list(CSV_FILES.keys())}")
            sys.exit(1)
        df   = pd.read_csv(os.path.join(args.csv, CSV_FILES[args.cls]))
        cols = SUBJECT_COLS[args.cls]
        for _, row in df.head(args.n).iterrows():
            sd   = row_to_student_data(row, cols)
            path = os.path.join(args.out, args.cls, f"{sd['student_id']}.pdf")
            create_report_card(sd, path)
            print(f"  ✓  {sd['name']}  ({sd['student_id']})")

    elif args.all:
        print("Generating all report cards …")
        generate_batch(args.csv, args.out)

    else:   # default: demo
        print("Generating demo (rank #1 student per class) …")
        generate_demo(args.csv, args.out)
