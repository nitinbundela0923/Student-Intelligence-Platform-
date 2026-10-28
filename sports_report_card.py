"""
sports_report_card.py

Production-ready Sports Report Card PDF generator built with ReportLab Platypus.

Public API:
    generate_sports_report(student: dict, output_pdf: str) -> None

Author: Senior Python Developer / PDF Designer
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas as pdf_canvas


# ============================================================
# CONSTANTS / THEME
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

MARGIN_LEFT = 16 * mm
MARGIN_RIGHT = 16 * mm
MARGIN_TOP = 14 * mm
MARGIN_BOTTOM = 14 * mm

CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

COLOR_BLACK = colors.HexColor("#111111")
COLOR_DARK = colors.HexColor("#1a1a1a")
COLOR_LIGHT_GREY = colors.HexColor("#f2f2f2")
COLOR_MID_GREY = colors.HexColor("#d9d9d9")
COLOR_BORDER = colors.HexColor("#333333")
COLOR_ACCENT = colors.HexColor("#2e7d32")  # green accent for sports theme
COLOR_ACCENT_LIGHT = colors.HexColor("#e8f5e9")
COLOR_WHITE = colors.white


# ============================================================
# STYLES
# ============================================================

def _build_styles():
    """Return a dict of ParagraphStyle objects used across the document."""
    styles = {}

    styles["school_name"] = ParagraphStyle(
        "SchoolName",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=COLOR_BLACK,
        spaceAfter=2,
    )

    styles["report_title"] = ParagraphStyle(
        "ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=COLOR_ACCENT,
        spaceAfter=0,
    )

    styles["section_header"] = ParagraphStyle(
        "SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        alignment=TA_LEFT,
        textColor=COLOR_WHITE,
    )

    styles["label"] = ParagraphStyle(
        "Label",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=COLOR_BLACK,
    )

    styles["value"] = ParagraphStyle(
        "Value",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=COLOR_BLACK,
    )

    styles["table_header"] = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=COLOR_WHITE,
    )

    styles["table_cell"] = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=COLOR_BLACK,
    )

    styles["table_cell_left"] = ParagraphStyle(
        "TableCellLeft",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=COLOR_BLACK,
    )

    styles["remarks_text"] = ParagraphStyle(
        "RemarksText",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=COLOR_BLACK,
    )

    styles["grade_text"] = ParagraphStyle(
        "GradeText",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=COLOR_ACCENT,
    )

    styles["grade_caption"] = ParagraphStyle(
        "GradeCaption",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=COLOR_BLACK,
    )

    styles["signature_label"] = ParagraphStyle(
        "SignatureLabel",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=COLOR_BLACK,
    )

    styles["footer_note"] = ParagraphStyle(
        "FooterNote",
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
    )

    return styles


# ============================================================
# HELPERS - DATA NORMALIZATION
# ============================================================

def _safe_get(student, key, default="N/A"):
    """Safely fetch a value from the student dict, falling back to default."""
    value = student.get(key, default)
    if value is None or value == "":
        return default
    return value


def _yes_no(value):
    """Normalize truthy/falsy sports participation values into Yes/No text."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("yes", "true", "1", "y"):
            return "Yes"
        if v in ("no", "false", "0", "n"):
            return "No"
        return value
    if isinstance(value, (int, float)):
        return "Yes" if value else "No"
    return "N/A"


def _fmt_hours(value):
    """Format sports hours per week value with unit suffix."""
    if value in (None, "", "N/A"):
        return "N/A"
    try:
        num = float(value)
        if num == int(num):
            num = int(num)
        return f"{num} Hours"
    except (ValueError, TypeError):
        return str(value)


def _fmt_percentage(value):
    """Format a percentage-like value with a trailing % sign."""
    if value in (None, "", "N/A"):
        return "N/A"
    try:
        num = float(value)
        if num == int(num):
            num = int(num)
        return f"{num}%"
    except (ValueError, TypeError):
        return str(value)


def _fmt_count(value, singular="", plural=""):
    """Format a count value, optionally appending a unit label."""
    if value in (None, "", "N/A"):
        return "N/A"
    try:
        num = float(value)
        if num == int(num):
            num = int(num)
        if singular or plural:
            unit = singular if num == 1 else plural
            return f"{num} {unit}".strip()
        return str(num)
    except (ValueError, TypeError):
        return str(value)


def _fitness_level(student):
    """Derive a qualitative fitness level from available metrics."""
    if "Fitness_Level" in student and student.get("Fitness_Level"):
        return str(student["Fitness_Level"])
    try:
        hours = float(student.get("Sports_Hours_Per_Week", 0) or 0)
    except (ValueError, TypeError):
        hours = 0
    if hours >= 8:
        return "Excellent"
    if hours >= 6:
        return "Very Good"
    if hours >= 4:
        return "Good"
    if hours >= 2:
        return "Fair"
    return "Needs Improvement"


def _team_work(student):
    """Derive a teamwork rating based on school team membership."""
    if "Team_Work" in student and student.get("Team_Work"):
        return str(student["Team_Work"])
    member = _yes_no(student.get("School_Team_Member"))
    return "Strong" if member == "Yes" else "Developing"


def _discipline(student):
    """Derive a discipline rating from attendance percentage."""
    if "Discipline" in student and student.get("Discipline"):
        return str(student["Discipline"])
    try:
        att = float(student.get("Attendance_Percentage", 0) or 0)
    except (ValueError, TypeError):
        att = 0
    if att >= 90:
        return "Excellent"
    if att >= 75:
        return "Good"
    if att >= 60:
        return "Satisfactory"
    return "Needs Improvement"


def _leadership(student):
    """Derive a leadership rating from school team membership / competitions."""
    if "Leadership" in student and student.get("Leadership"):
        return str(student["Leadership"])
    member = _yes_no(student.get("School_Team_Member"))
    try:
        comps = float(student.get("Competitions_Attended", 0) or 0)
    except (ValueError, TypeError):
        comps = 0
    if member == "Yes" and comps >= 3:
        return "Demonstrated"
    if member == "Yes" or comps >= 1:
        return "Emerging"
    return "Not Yet Demonstrated"


def _calculate_sports_hours(student):
    """Return numeric sports hours per week, defaulting to 0."""
    try:
        return float(student.get("Sports_Hours_Per_Week", 0) or 0)
    except (ValueError, TypeError):
        return 0.0


def _calculate_grade(sports_hours):
    """Calculate overall sports grade based on weekly sports hours."""
    if sports_hours >= 8:
        return "A+"
    if sports_hours >= 6:
        return "A"
    if sports_hours >= 4:
        return "B+"
    if sports_hours >= 2:
        return "B"
    return "C"


def _generate_remarks(student):
    """
    Auto-generate coach remarks based on the student's sports data.
    Produces 2-4 sentences summarizing performance.
    """
    remarks = []

    hours = _calculate_sports_hours(student)
    participation = _yes_no(student.get("Sports_Participation"))
    team_member = _yes_no(student.get("School_Team_Member"))

    try:
        attendance = float(student.get("Attendance_Percentage", 0) or 0)
    except (ValueError, TypeError):
        attendance = 0

    try:
        competitions = float(student.get("Competitions_Attended", 0) or 0)
    except (ValueError, TypeError):
        competitions = 0

    medals = _safe_get(student, "Medals_or_Certificates", "")

    # Participation & effort
    if participation == "Yes" and hours >= 6:
        remarks.append("Excellent participation and discipline in all sporting activities.")
    elif participation == "Yes" and hours >= 3:
        remarks.append("Good participation with consistent effort shown throughout the term.")
    elif participation == "Yes":
        remarks.append("Shows interest in sports activities; participation should be increased.")
    else:
        remarks.append("Participation in sports activities has been minimal this term.")

    # Teamwork & leadership
    if team_member == "Yes":
        remarks.append("Shows strong teamwork and leadership qualities as a school team member.")
    else:
        remarks.append("Encouraged to join a school team to further develop teamwork skills.")

    # Attendance & discipline
    if attendance >= 90:
        remarks.append("Maintains excellent attendance and discipline during practice sessions.")
    elif attendance >= 75:
        remarks.append("Maintains good attendance with room for further consistency.")
    else:
        remarks.append("Attendance at practice sessions needs improvement.")

    # Competitions & achievements
    if competitions >= 3 or (medals and medals not in ("N/A", "", "None")):
        remarks.append("Eligible for inter-school competitions based on current performance and achievements.")
    elif competitions >= 1:
        remarks.append("Has represented the school in competitions; continued growth is encouraged.")
    else:
        remarks.append("Encouraged to take part in upcoming competitions to gain experience.")

    return " ".join(remarks)


# ============================================================
# HELPERS - FLOWABLE BUILDERS
# ============================================================

def _section_header_table(title, styles, width=CONTENT_WIDTH):
    """Build a full-width black section header bar as a single-cell table."""
    data = [[Paragraph(title.upper(), styles["section_header"])]]
    t = Table(data, colWidths=[width])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_BLACK),
                ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_WHITE),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return t


def _build_header(styles, story):
    """Append the report header (school name, title, divider) to the story."""
    story.append(Paragraph("MACRO VISION ACADEMY", styles["school_name"]))
    story.append(Paragraph("SPORTS REPORT CARD", styles["report_title"]))
    story.append(Spacer(1, 6))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.4,
            color=COLOR_BLACK,
            spaceBefore=2,
            spaceAfter=10,
        )
    )


def _build_student_info(student, styles, story):
    """Append the two-column student information block to the story."""
    story.append(_section_header_table("Student Information", styles))
    story.append(Spacer(1, 6))

    left_rows = [
        ("Student Name", _safe_get(student, "Student_Name")),
        ("Student ID", _safe_get(student, "Student_ID")),
        ("Class", _safe_get(student, "Class")),
        ("Section", _safe_get(student, "Section")),
    ]
    right_rows = [
        ("Academic Year", _safe_get(student, "Academic_Year")),
        ("Sports Coach", _safe_get(student, "Sports_Coach")),
        ("Age", _safe_get(student, "Age")),
        ("Gender", _safe_get(student, "Gender")),
    ]

    col_w = CONTENT_WIDTH / 2.0
    label_w = col_w * 0.34
    value_w = col_w * 0.66

    table_data = []
    for (l_label, l_value), (r_label, r_value) in zip(left_rows, right_rows):
        table_data.append(
            [
                Paragraph(f"{l_label} :", styles["label"]),
                Paragraph(str(l_value), styles["value"]),
                Paragraph(f"{r_label} :", styles["label"]),
                Paragraph(str(r_value), styles["value"]),
            ]
        )

    info_table = Table(
        table_data,
        colWidths=[label_w, value_w, label_w, value_w],
    )
    info_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -2), 0.4, COLOR_MID_GREY),
                ("BOX", (0, 0), (-1, -1), 0.8, COLOR_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, COLOR_MID_GREY),
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_WHITE),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 12))


def _build_performance_table(student, styles, story):
    """Append the sports performance quarterly table to the story."""
    story.append(_section_header_table("Sports Performance", styles))
    story.append(Spacer(1, 6))

    hours_val = _calculate_sports_hours(student)

    rows_config = [
        ("Sports Participation", _yes_no(student.get("Sports_Participation"))),
        ("Sports Hours / Week", _fmt_hours(student.get("Sports_Hours_Per_Week"))),
        ("Fitness Level", _fitness_level(student)),
        ("Team Work", _team_work(student)),
        ("Discipline", _discipline(student)),
        ("Leadership", _leadership(student)),
        ("Competitions", _fmt_count(student.get("Competitions_Attended"))),
        ("Achievements", _safe_get(student, "Medals_or_Certificates", "None")),
        ("Attendance", _fmt_percentage(student.get("Attendance_Percentage"))),
    ]

    header = ["Category", "Q1", "Q2", "Q3", "Q4", "Final"]
    table_data = [[Paragraph(h, styles["table_header"]) for h in header]]

    quarter_keys = {
        "Sports Participation": ["Q1_Participation", "Q2_Participation", "Q3_Participation", "Q4_Participation"],
        "Sports Hours / Week": ["Q1_Hours", "Q2_Hours", "Q3_Hours", "Q4_Hours"],
        "Fitness Level": ["Q1_Fitness", "Q2_Fitness", "Q3_Fitness", "Q4_Fitness"],
        "Team Work": ["Q1_TeamWork", "Q2_TeamWork", "Q3_TeamWork", "Q4_TeamWork"],
        "Discipline": ["Q1_Discipline", "Q2_Discipline", "Q3_Discipline", "Q4_Discipline"],
        "Leadership": ["Q1_Leadership", "Q2_Leadership", "Q3_Leadership", "Q4_Leadership"],
        "Competitions": ["Q1_Competitions", "Q2_Competitions", "Q3_Competitions", "Q4_Competitions"],
        "Achievements": ["Q1_Achievements", "Q2_Achievements", "Q3_Achievements", "Q4_Achievements"],
        "Attendance": ["Q1_Attendance", "Q2_Attendance", "Q3_Attendance", "Q4_Attendance"],
    }

    for label, final_value in rows_config:
        keys = quarter_keys.get(label, [])
        quarter_values = []
        for k in keys:
            v = student.get(k, None)
            quarter_values.append(str(v) if v not in (None, "") else "-")

        row = [Paragraph(label, styles["table_cell_left"])]
        row += [Paragraph(qv, styles["table_cell"]) for qv in quarter_values]
        row.append(Paragraph(str(final_value), styles["table_cell"]))
        table_data.append(row)

    col_widths = [
        CONTENT_WIDTH * 0.30,
        CONTENT_WIDTH * 0.12,
        CONTENT_WIDTH * 0.12,
        CONTENT_WIDTH * 0.12,
        CONTENT_WIDTH * 0.12,
        CONTENT_WIDTH * 0.22,
    ]

    perf_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_BLACK),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_WHITE),
        ("BOX", (0, 0), (-1, -1), 0.9, COLOR_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), COLOR_LIGHT_GREY))
        else:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), COLOR_WHITE))

    perf_table.setStyle(TableStyle(style_cmds))
    story.append(perf_table)
    story.append(Spacer(1, 12))

    return hours_val


def _build_attendance_and_remarks(student, styles, story):
    """Append side-by-side Attendance table and Coach Remarks box to the story."""
    # ---- Attendance table (left column) ----
    att_header_table = _section_header_table(
        "Attendance", styles, width=CONTENT_WIDTH * 0.46
    )

    att_rows = [
        ("Sports Attendance", _fmt_percentage(student.get("Attendance_Percentage"))),
        ("Practice Sessions", _fmt_hours(student.get("Sports_Hours_Per_Week"))),
        ("Competitions", _fmt_count(student.get("Competitions_Attended"))),
        ("Certificates", _safe_get(student, "Medals_or_Certificates", "None")),
    ]
    att_data = [
        [Paragraph(label, styles["table_cell_left"]), Paragraph(str(value), styles["table_cell"])]
        for label, value in att_rows
    ]
    att_table = Table(
        att_data,
        colWidths=[CONTENT_WIDTH * 0.46 * 0.55, CONTENT_WIDTH * 0.46 * 0.45],
    )
    att_style_cmds = [
        ("BOX", (0, 0), (-1, -1), 0.9, COLOR_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(len(att_data)):
        bg = COLOR_LIGHT_GREY if i % 2 == 0 else COLOR_WHITE
        att_style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    att_table.setStyle(TableStyle(att_style_cmds))

    attendance_block = [att_header_table, Spacer(1, 6), att_table]

    # ---- Coach remarks (right column) ----
    remarks_header_table = _section_header_table(
        "Coach Remarks", styles, width=CONTENT_WIDTH * 0.50
    )
    remarks_text = _generate_remarks(student)
    remarks_para = Paragraph(remarks_text, styles["remarks_text"])
    remarks_box = Table(
        [[remarks_para]],
        colWidths=[CONTENT_WIDTH * 0.50],
        rowHeights=[None],
        minRowHeights=[32 * mm],
    )
    remarks_box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.9, COLOR_BORDER),
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_WHITE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    remarks_block = [remarks_header_table, Spacer(1, 6), remarks_box]

    # ---- Combine into a two-column outer table ----
    outer_table = Table(
        [[attendance_block, remarks_block]],
        colWidths=[CONTENT_WIDTH * 0.46, CONTENT_WIDTH * 0.50],
    )
    outer_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 8),
                ("LEFTPADDING", (1, 0), (1, 0), 0),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(outer_table)
    story.append(Spacer(1, 12))


def _build_overall_grade(sports_hours, styles, story):
    """Append the highlighted overall sports grade box to the story."""
    story.append(_section_header_table("Overall Sports Grade", styles))
    story.append(Spacer(1, 6))

    grade = _calculate_grade(sports_hours)

    caption = Paragraph(
        f"Based on {sports_hours:g} hrs/week of sports activity", styles["grade_caption"]
    )
    grade_para = Paragraph(grade, styles["grade_text"])

    grade_table = Table(
        [[grade_para], [caption]],
        colWidths=[CONTENT_WIDTH],
    )
    grade_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.2, COLOR_ACCENT),
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_ACCENT_LIGHT),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (0, 0), 8),
                ("BOTTOMPADDING", (0, 0), (0, 0), 2),
                ("TOPPADDING", (0, 1), (0, 1), 0),
                ("BOTTOMPADDING", (0, 1), (0, 1), 8),
            ]
        )
    )
    story.append(grade_table)
    story.append(Spacer(1, 14))


def _build_signatures(styles, story):
    """Append the three signature boxes (teacher, coordinator, principal)."""
    story.append(_section_header_table("Signatures", styles))
    story.append(Spacer(1, 10))

    col_w = CONTENT_WIDTH / 3.0
    labels = ["Sports Teacher", "Sports Coordinator", "Principal"]

    line_row = []
    label_row = []
    for _ in labels:
        line_row.append("")
        label_row.append("")

    # Build a table with a blank signature line row and a label row beneath it
    sig_data = [
        [Paragraph("&nbsp;", styles["value"]) for _ in labels],
        [Paragraph(lbl, styles["signature_label"]) for lbl in labels],
    ]
    sig_table = Table(sig_data, colWidths=[col_w] * 3, rowHeights=[16 * mm, 8 * mm])
    sig_style_cmds = [
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LINEBELOW", (0, 0), (0, 0), 0.9, COLOR_BORDER),
        ("LINEBELOW", (1, 0), (1, 0), 0.9, COLOR_BORDER),
        ("LINEBELOW", (2, 0), (2, 0), 0.9, COLOR_BORDER),
        ("TOPPADDING", (0, 0), (-1, 0), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]
    sig_table.setStyle(TableStyle(sig_style_cmds))
    story.append(sig_table)


# ============================================================
# PAGE DECORATION (BORDER / FOOTER)
# ============================================================

def _make_on_page(student):
    """
    Return an on_page callback that draws a subtle page border and a footer
    on every page of the document.
    """

    def _on_page(canvas_obj: pdf_canvas.Canvas, doc):
        canvas_obj.saveState()

        # Outer page border
        border_margin = 8 * mm
        canvas_obj.setStrokeColor(COLOR_MID_GREY)
        canvas_obj.setLineWidth(0.8)
        canvas_obj.rect(
            border_margin,
            border_margin,
            PAGE_WIDTH - 2 * border_margin,
            PAGE_HEIGHT - 2 * border_margin,
        )

        # Footer text
        canvas_obj.setFont("Helvetica-Oblique", 7.5)
        canvas_obj.setFillColor(colors.HexColor("#666666"))
        footer_text = (
            f"Macro Vision Academy | Sports Report Card | "
            f"Generated for {student.get('Student_Name', 'Student')}"
        )
        canvas_obj.drawCentredString(PAGE_WIDTH / 2.0, 10 * mm, footer_text)

        canvas_obj.restoreState()

    return _on_page


# ============================================================
# PUBLIC API
# ============================================================

def generate_sports_report(student: dict, output_pdf: str) -> None:
    """
    Generate a single-page Sports Report Card PDF for the given student.

    Parameters
    ----------
    student : dict
        Dictionary containing student and sports performance data. Expected
        (optional) keys include:
            Student_Name, Student_ID, Class, Section, Age, Gender,
            Academic_Year, Sports_Coach, Favorite_Sport,
            Sports_Participation, Sports_Hours_Per_Week,
            School_Team_Member, Competitions_Attended,
            Medals_or_Certificates, Attendance_Percentage, Percentage,
            plus optional per-quarter keys such as Q1_Participation,
            Q2_Hours, etc.
    output_pdf : str
        File path where the generated PDF will be written.

    Returns
    -------
    None
    """
    if not isinstance(student, dict):
        raise TypeError("student must be a dictionary")
    if not output_pdf:
        raise ValueError("output_pdf path must be provided")

    styles = _build_styles()

    doc = BaseDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="Sports Report Card",
        author="Macro Vision Academy",
    )

    frame = Frame(
        MARGIN_LEFT,
        MARGIN_BOTTOM,
        CONTENT_WIDTH,
        PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM,
        id="main_frame",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )

    template = PageTemplate(id="report_page", frames=[frame], onPage=_make_on_page(student))
    doc.addPageTemplates([template])

    story = []

    _build_header(styles, story)
    _build_student_info(student, styles, story)
    sports_hours = _build_performance_table(student, styles, story)
    _build_attendance_and_remarks(student, styles, story)
    _build_overall_grade(sports_hours, styles, story)
    _build_signatures(styles, story)

    doc.build(story)


# ============================================================
# MANUAL TEST (only runs when executed directly)
# ============================================================

if __name__ == "__main__":
    sample_student = {
        "Student_Name": "Ethan Carter",
        "Student_ID": "MVA-2026-0142",
        "Class": "10",
        "Section": "B",
        "Age": 15,
        "Gender": "Male",
        "Academic_Year": "2025 - 2026",
        "Sports_Coach": "Mr. Daniel Reyes",
        "Favorite_Sport": "Basketball",
        "Sports_Participation": "Yes",
        "Sports_Hours_Per_Week": 6,
        "School_Team_Member": "Yes",
        "Competitions_Attended": 4,
        "Medals_or_Certificates": "Gold Medal",
        "Attendance_Percentage": 92,
        "Percentage": 88,
    }

    generate_sports_report(sample_student, "sample_sports_report_card.pdf")
    print("Sample report generated: sample_sports_report_card.pdf")
