"""
Tower Clash: Diamonds & Kings — PDF Generator
Generates printable game track and cheat sheet.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth


def generate_printables(out_path="Tower_Clash_Printables.pdf"):
    """
    Generate a PDF with:
    - Page 1: Game track (0-20 steps) for 4 players
    - Page 2: One-page cheat sheet with all rules
    """
    W, H = A4
    margin = 14 * mm

    c = canvas.Canvas(out_path, pagesize=A4)
    c.setTitle("Tower Clash: Diamonds & Kings — Printables")

    def draw_header(title, subtitle=None):
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, H - margin - 8, title)
        if subtitle:
            c.setFont("Helvetica", 10.2)
            c.setFillColor(colors.grey)
            c.drawString(margin, H - margin - 26, subtitle)
            c.setFillColor(colors.black)

    # -------- PAGE 1: TRACK --------
    draw_header(
        "Tower Track (0-20 steps)",
        "Print and use coins/pawns as markers. First to reach 20 steps wins (or change the goal in your house rules)."
    )

    lane_count = 4
    usable_w = W - 2 * margin
    lane_w = usable_w / lane_count

    track_bottom = margin + 18 * mm
    track_top = H - margin - 40 * mm
    track_h = track_top - track_bottom

    steps_max = 20
    cells = steps_max + 1
    cell_h = track_h / cells

    for i in range(lane_count):
        x0 = margin + i * lane_w
        c.setFillColor(colors.whitesmoke if i % 2 == 0 else colors.Color(0.97, 0.97, 0.97))
        c.rect(x0, track_bottom, lane_w, track_h, fill=1, stroke=0)
        c.setStrokeColor(colors.lightgrey)
        c.rect(x0, track_bottom, lane_w, track_h, fill=0, stroke=1)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x0 + lane_w / 2, track_top + 10, f"Player {i+1}")

    for step in range(cells):
        y = track_bottom + step * cell_h
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.6)
        c.line(margin, y, margin + usable_w, y)

    for step in range(0, cells, 5):
        y = track_bottom + step * cell_h
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1.2)
        c.line(margin, y, margin + usable_w, y)

    for i in range(lane_count):
        x0 = margin + i * lane_w
        for step in range(cells):
            y = track_bottom + step * cell_h
            c.setFillColor(colors.darkgrey if step % 5 else colors.black)
            c.setFont("Helvetica-Bold" if step % 5 == 0 else "Helvetica", 8.5)
            c.drawString(x0 + 3, y + 2, str(step))

    banner_h = 12 * mm
    c.setFillColor(colors.Color(0.1, 0.1, 0.1))
    c.roundRect(margin, track_top + 18, usable_w, banner_h, 6, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(margin + usable_w / 2, track_top + 18 + banner_h / 2 - 4, "GOAL: 20 STEPS")

    legend_y = margin + 6 * mm
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, legend_y + 18, "Quick legend")
    c.setFont("Helvetica", 9.5)
    c.drawString(margin, legend_y + 6, "Move your marker up or down based on combos. Minimum is 0 steps (cannot go below 0).")

    c.setStrokeColor(colors.lightgrey)
    c.setDash(2, 2)
    for i in range(1, lane_count):
        x = margin + i * lane_w
        c.line(x, track_bottom, x, track_bottom + track_h)
    c.setDash()

    c.showPage()

    # -------- PAGE 2: CHEAT SHEET --------
    draw_header(
        "One-page Cheat Sheet — Tower Clash: Diamonds & Kings",
        "All combos require same rank (A,2...K). Diamonds are public at end of turn; spent diamonds go to discard."
    )

    # Helpers for wrapped text (manual, reliable)
    def wrap_lines(text, font_name, font_size, max_w):
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if stringWidth(test, font_name, font_size) <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def draw_block(x, y, max_w, lines, font="Helvetica", size=9.2, leading=12):
        c.setFont(font, size)
        for line in lines:
            c.drawString(x, y, line)
            y -= leading
        return y

    def h2(x, y, title):
        c.setFont("Helvetica-Bold", 11.5)
        c.setFillColor(colors.black)
        c.drawString(x, y, title)
        return y - 16

    left_x = margin
    right_x = W / 2 + 6 * mm
    col_w = W / 2 - margin - 8 * mm
    y_start = H - margin - 56
    leading = 12

    # LEFT COLUMN
    y = y_start
    y = h2(left_x, y, "Card roles")
    y = draw_block(left_x, y, col_w, wrap_lines("♥ = Positive.  ♠/♣ = Black (negative).  ♦ = Neutral (special).", "Helvetica", 9.2, col_w), "Helvetica", 9.2, leading)
    y -= 2
    y = draw_block(left_x, y, col_w, wrap_lines("Diamonds: At end of every turn, move all ♦ you have to the Public Diamond Row (face up).", "Helvetica", 9.2, col_w), "Helvetica", 9.2, leading)
    y = draw_block(left_x, y, col_w, wrap_lines("You may use public ♦ in combos; used ♦ are discarded.", "Helvetica", 9.2, col_w), "Helvetica", 9.2, leading)

    y -= 6
    y = h2(left_x, y, "Turn (very short)")
    turn_text = [
        "1) Draw 1.",
        "2) Optional: Skip-turn cycle: discard 1, draw 1 (if discarded is ♦, you may repeat) and end turn.",
        "3) Otherwise: play cards, cash-in combos, Diamond Swap (once), Diamond Command, 6♦ Jackpot.",
        "4) End: if hand is 0 -> lose 1 step (min 0) and draw 6. Then reveal all ♦ to board."
    ]
    for t in turn_text:
        y = draw_block(left_x, y, col_w, wrap_lines(t, "Helvetica", 9.2, col_w), "Helvetica", 9.2, leading)
    y -= 4

    y = h2(left_x, y, "Combos (same rank)")
    combo_rows = [
        ("♠ + ♣ (two blacks)", "+1 step"),
        ("♥ + (♠ or ♣)", "+2 steps"),
        ("♥ + ♠ + ♣", "+3 steps"),
        ("♥ + ♦", "+1 step, draw 1"),
        ("♦ + (♠ or ♣)", "discard 1, draw 1"),
        ("3 cards incl. ♦", "+1 step, discard 1, draw 1"),
        ("4 of a kind", "+3 steps, draw 1"),
    ]
    c.setFont("Helvetica-Bold", 9.2)
    for lbl, eff in combo_rows:
        c.setFont("Helvetica-Bold", 9.2)
        c.drawString(left_x, y, lbl)
        c.setFont("Helvetica", 9.2)
        c.drawString(left_x + 165, y, eff)
        y -= 13

    y -= 6
    king_note = "King note: If the combo rank is K, double the step gain (draw/discard stays the same), except Four Kings special."
    y = draw_block(left_x, y, col_w, wrap_lines(king_note, "Helvetica-Oblique", 9.0, col_w), "Helvetica-Oblique", 9.0, 11.5)

    # RIGHT COLUMN
    y2 = y_start
    y2 = h2(right_x, y2, "Diamond actions")
    diamond_lines = [
        "• Swap (once/turn): swap ownership of 1 of your public ♦ with 1 public ♦ of another player.",
        "• Command (pay 1♦): force target discard 1. If black: target -1 step. If heart: you +1 step.",
        "  If diamond: Round 1 target draws 1; after Round 1 -> Hoarding Penalty.",
        "• Hoarding Penalty (after Round 1): if a player discards a ♦ from hand: discard all hand cards, discard all owned public ♦, -1 step, draw 6.",
        "• 6♦ Jackpot: if you have 6 diamonds total (Round 1 hand + owned public): +6 steps, discard 6♦, refill hand to 6."
    ]
    for t in diamond_lines:
        y2 = draw_block(right_x, y2, col_w, wrap_lines(t, "Helvetica", 9.2, col_w), "Helvetica", 9.2, leading)
    y2 -= 4

    y2 = h2(right_x, y2, "Kings (K) special")
    king_lines = [
        "• Four Kings: K♥ + K♠ + K♣ + K♦ -> +6 steps and draw 2.",
        "• Discarded King: whenever a King is discarded as a cost/effect:",
        "  black K -> discarder -2 steps; heart K -> discarder +2 steps; diamond K -> discarder draws 2."
    ]
    for t in king_lines:
        y2 = draw_block(right_x, y2, col_w, wrap_lines(t, "Helvetica", 9.2, col_w), "Helvetica", 9.2, leading)
    y2 -= 4

    y2 = h2(right_x, y2, "Win")
    y2 = draw_block(right_x, y2, col_w, wrap_lines("First player to reach 20 steps wins immediately (or 15/30 for shorter/longer games).", "Helvetica", 9.2, col_w), "Helvetica", 9.2, leading)

    # Footer
    c.setStrokeColor(colors.lightgrey)
    c.line(margin, margin + 10, W - margin, margin + 10)
    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 8.5)
    c.drawString(margin, margin, "Tower Clash: Diamonds & Kings — Printable Track + Cheat Sheet")
    c.drawRightString(W - margin, margin, "v1")

    c.save()
    return out_path


if __name__ == "__main__":
    output = generate_printables("Tower_Clash_Printables.pdf")
    print(f"✓ PDF generated: {output}")
