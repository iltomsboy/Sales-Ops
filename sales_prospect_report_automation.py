# =============================================================================
# Hotel Revenue Opportunity Simulation
# Monte Carlo Simulation + PDF Report Generator
# =============================================================================
# Note: API integration is stubbed out (see get_ai_visibility).
#       Replace API_KEY and endpoint URL before enabling.
# =============================================================================

import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from google.colab import drive, files
import ipywidgets as widgets
from IPython.display import display


# =============================================================================
# CONFIGURATION
# =============================================================================

# API_KEY = "your_key"  # Disabled — add your key here before use

SALES_NAME  = "Marco Rossi"
SALES_EMAIL = "m.rossi@customeralliance.com"

PDF_PATH   = "hotel_report.pdf"
CHART_PATH = "monte_carlo_chart.png"
LOGO_PATH  = "/content/drive/MyDrive/DS - sales ops/company_logo.png"


# =============================================================================
# COLOR PALETTE
# =============================================================================

PRIMARY_BLUE = colors.HexColor("#0099CC")
DARK_BLUE    = colors.HexColor("#0D2137")
ACCENT       = colors.HexColor("#00C8FF")
TURQUOISE    = colors.HexColor("#3BE0D0")
LIGHT        = colors.HexColor("#F0F8FC")
LIGHT2       = colors.HexColor("#E3F3F9")
WHITE        = colors.HexColor("#FFFFFF")
GRAY_TEXT    = colors.HexColor("#4A5568")
GRAY_LINE    = colors.HexColor("#C4D9E5")


# =============================================================================
# API — AI VISIBILITY SCORE (disabled)
# =============================================================================

def get_ai_visibility(hotel_name, website):
    """
    Calls an external API to retrieve the AI visibility score for a hotel.
    Disabled by default — uncomment API_KEY and the call in main to enable.
    """
    # headers = {"Authorization": f"Bearer {API_KEY}"}
    # payload = {"hotel_name": hotel_name, "website": website}
    # response = requests.post(
    #     "https://api.somevisibilitytool.com/visibility",
    #     headers=headers,
    #     json=payload
    # )
    # return response.json()
    pass


# =============================================================================
# MONTE CARLO SIMULATION
# =============================================================================

def run_monte_carlo(rooms, adr, occupancy, n_simulations=10000):
    """
    Simulates annual revenue across n_simulations iterations by applying
    random uplifts to occupancy based on three improvement levers:
      - AI visibility improvement
      - Rating improvement
      - Review response rate improvement

    Returns:
        results (list): all simulated revenue values
        percentiles (tuple): (p25, p50, p90) — conservative / expected / aggressive
    """
    results = []

    for _ in range(n_simulations):

        visibility_uplift = random.uniform(0, 0.050)  # AI visibility impact
        rating_uplift     = random.uniform(0, 0.008)  # Rating impact
        response_uplift   = random.uniform(0, 0.030)  # Review response impact

        new_occupancy = (
            occupancy
            * (1 + visibility_uplift)
            * (1 + rating_uplift)
            * (1 + response_uplift)
        )

        revenue = rooms * adr * new_occupancy * 365
        results.append(revenue)

    p25 = round(np.percentile(results, 25), 2)  # Conservative
    p50 = round(np.percentile(results, 50), 2)  # Expected
    p90 = round(np.percentile(results, 90), 2)  # Aggressive

    return results, (p25, p50, p90)


# =============================================================================
# CHART
# =============================================================================

def plot_simulation(hotel_name, current_revenue, simulated_revenue, percentiles):
    """
    Plots the Monte Carlo revenue distribution with reference lines for
    current revenue and the three scenario percentiles. Saves to CHART_PATH.
    """
    plt.rcParams["font.family"] = "sans-serif"
    sns.set_theme(style="white", context="talk")

    plt.figure(figsize=(18, 9))

    sns.histplot(
        simulated_revenue,
        bins=40,
        kde=True,
        color="#0099CC",
        alpha=0.55,
        edgecolor="white",
        linewidth=0.5
    )

    plt.axvline(
        current_revenue,
        color="#00C8FF",
        linestyle=":",
        linewidth=4,
        label=f"Current Revenue: €{current_revenue:,.0f}"
    )
    plt.axvline(
        percentiles[0],
        color="#0D2137",
        linestyle="--",
        linewidth=3,
        label=f"Conservative: €{percentiles[0]:,.0f}"
    )
    plt.axvline(
        percentiles[1],
        color="#0099CC",
        linestyle="-",
        linewidth=4,
        label=f"Expected: €{percentiles[1]:,.0f}"
    )
    plt.axvline(
        percentiles[2],
        color="#0D2137",
        linestyle="--",
        linewidth=3,
        label=f"Aggressive: €{percentiles[2]:,.0f}"
    )

    plt.title(
        "Monte Carlo Revenue Opportunity Simulation",
        fontsize=24, fontweight="bold", color="#0D2137", pad=25
    )
    plt.suptitle(
        f"Potential Revenue Impact for {hotel_name}",
        fontsize=14, color="#4A5568", y=0.95
    )
    plt.xlabel("Annual Revenue (€)", fontsize=14, color="#4A5568")
    plt.ylabel("Simulation Frequency", fontsize=14, color="#4A5568")
    plt.legend(fontsize=12, frameon=True, fancybox=True,
               facecolor="#FFFFFF", edgecolor="#C4D9E5", loc="upper left")
    plt.grid(False)
    sns.despine(left=False, bottom=False)
    plt.tight_layout()
    plt.savefig(CHART_PATH, bbox_inches="tight", dpi=150)
    plt.show()


# =============================================================================
# PDF REPORT — HELPERS
# =============================================================================

def fill_rect(c, x, y, w, h, color, radius=0):
    c.setFillColor(color)
    c.setStrokeColor(color)
    if radius:
        c.roundRect(x, y, w, h, radius, stroke=0, fill=1)
    else:
        c.rect(x, y, w, h, stroke=0, fill=1)


def section_title(c, x, y, text, font_size=13):
    c.setFillColor(DARK_BLUE)
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(x, y, text)


def h_line(c, x, y, w, color=GRAY_LINE, thickness=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(thickness)
    c.line(x, y, x + w, y)


# =============================================================================
# PDF REPORT — BUILDER
# =============================================================================

def generate_pdf(hotel_name, website, rooms, adr, occupancy,
                 current_revenue, percentiles):
    """
    Builds a single-page A4 PDF sales report including:
      - Header with logo and hotel info
      - Current performance metrics
      - Current annual revenue estimate
      - Three revenue scenarios (conservative / expected / aggressive)
      - Scenario comparison table
      - Monte Carlo chart
      - CTA and branded footer
    """
    today = datetime.today().strftime("%d %B %Y")

    pdf       = canvas.Canvas(PDF_PATH, pagesize=A4)
    width, height = A4  # 595 × 842 pt

    # --- Layout constants ---
    HEADER_H = 80
    ACCENT_H = 4
    FOOTER_H = 90
    CTA_H    = 58
    BODY_TOP = height - HEADER_H - ACCENT_H
    BODY_BOT = FOOTER_H + CTA_H
    PAD      = 30
    INNER_W  = width - PAD * 2
    GAP_T    = 16
    GAP_B    = 8
    COL_GAP  = 16
    COL_W    = (INNER_W - COL_GAP) / 2
    COL2_X   = PAD + COL_W + COL_GAP

    # --- Header ---
    fill_rect(pdf, 0, height - HEADER_H, width, HEADER_H, DARK_BLUE)
    try:
        pdf.drawImage(LOGO_PATH, PAD, height - HEADER_H + 14,
                      width=100, height=50,
                      preserveAspectRatio=True, mask="auto")
    except Exception:
        pass

    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(148, height - 37, "Hotel Revenue Opportunity Assessment")
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(ACCENT)
    pdf.drawString(148, height - 54, f"{hotel_name}  ·  {website}  ·  {today}")
    fill_rect(pdf, 0, height - HEADER_H - ACCENT_H, width, ACCENT_H, TURQUOISE)

    # --- Section 1: Current Performance (2-column) ---
    ROW_H = 21
    y = BODY_TOP - GAP_T
    section_title(pdf, PAD, y, "Current Performance", font_size=13)
    y -= (GAP_B + 12)

    metrics = [
        ("AI Visibility Score", 42),
        ("Average Rating",      4.3),
        ("Total Reviews",       1850),
        ("Reviews Per Month",   38),
        ("Response Rate",       "47%"),
        ("Property Rooms",      rooms),
    ]
    left_metrics  = metrics[:3]
    right_metrics = metrics[3:]
    top_y = y

    for col_idx, col_metrics in enumerate([left_metrics, right_metrics]):
        cx    = PAD   if col_idx == 0 else COL2_X
        cy    = top_y
        val_x = cx + 160
        for i, (label, value) in enumerate(col_metrics):
            if i % 2 == 0:
                fill_rect(pdf, cx - 4, cy - 3, COL_W + 4, ROW_H - 1, LIGHT)
            pdf.setFillColor(GRAY_TEXT)
            pdf.setFont("Helvetica", 9)
            pdf.drawString(cx, cy + 5, label)
            pdf.setFillColor(DARK_BLUE)
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(val_x, cy + 5, str(value))
            cy -= ROW_H

    PERF_BOT = top_y - (len(left_metrics) * ROW_H)

    # --- Section 2: Current Annual Revenue box ---
    y = PERF_BOT - GAP_T
    section_title(pdf, PAD, y, "Current Annual Revenue Estimation", font_size=13)
    y -= (GAP_B + 8)

    BOX_H = 76
    fill_rect(pdf, PAD - 4, y - BOX_H, INNER_W + 8, BOX_H, DARK_BLUE, radius=7)
    pdf.setFillColor(ACCENT)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(PAD + 4, y - 16, "CURRENT ANNUAL REVENUE ESTIMATION")
    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 36)
    pdf.drawString(PAD + 4, y - 60, f"€ {current_revenue:,.0f}")
    REV_BOT = y - BOX_H

    # --- Section 3: Revenue Scenarios (3 side-by-side boxes) ---
    y = REV_BOT - GAP_T
    section_title(pdf, PAD, y, "Revenue Scenarios", font_size=13)
    y -= (GAP_B + 8)

    BOX_W2 = (INNER_W - 12) / 3
    BOX_H2 = 72
    scenario_data = [
        ("Conservative", percentiles[0], colors.HexColor("#2BC4B4")),
        ("Expected",     percentiles[1], PRIMARY_BLUE),
        ("Aggressive",   percentiles[2], DARK_BLUE),
    ]

    for i, (label, rev, bg) in enumerate(scenario_data):
        bx = PAD + i * (BOX_W2 + 6)
        fill_rect(pdf, bx, y - BOX_H2, BOX_W2, BOX_H2, bg, radius=5)
        pdf.setFillColor(WHITE)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(bx + 10, y - 16, label)
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(bx + 10, y - 52, f"€ {rev:,.0f}")

    SCEN_BOT = y - BOX_H2

    # --- Section 4: Scenario Comparison Table ---
    y = SCEN_BOT - GAP_T + 4
    T_COLS  = [PAD, PAD + 130, PAD + 290, PAD + 420]
    T_HDR_H = 22
    T_ROW_H = 24

    fill_rect(pdf, PAD - 4, y - T_HDR_H, INNER_W + 8, T_HDR_H, DARK_BLUE, radius=3)
    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 10)
    for col, hdr in zip(T_COLS, ["Scenario", "Revenue (€)", "vs Current", "Uplift %"]):
        pdf.drawString(col, y - T_HDR_H + 7, hdr)

    ty = y - T_HDR_H - T_ROW_H
    for i, (label, rev) in enumerate([
        ("Conservative", percentiles[0]),
        ("Expected",     percentiles[1]),
        ("Aggressive",   percentiles[2]),
    ]):
        if i % 2 == 0:
            fill_rect(pdf, PAD - 4, ty - 3, INNER_W + 8, T_ROW_H - 1, LIGHT2)
        diff   = rev - current_revenue
        uplift = (diff / current_revenue * 100) if current_revenue else 0

        pdf.setFillColor(DARK_BLUE)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(T_COLS[0], ty + 7, label)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(T_COLS[1], ty + 7, f"{rev:,.0f}")
        pdf.setFillColor(PRIMARY_BLUE if diff >= 0 else colors.red)
        pdf.drawString(T_COLS[2], ty + 7,
                       f"+ € {diff:,.0f}" if diff >= 0 else f"- € {abs(diff):,.0f}")
        pdf.setFillColor(DARK_BLUE)
        pdf.drawString(T_COLS[3], ty + 7,
                       f"+ {uplift:.1f}%" if uplift >= 0 else f"{uplift:.1f}%")
        ty -= T_ROW_H

    h_line(pdf, PAD - 4, ty + 4, INNER_W + 8)
    TAB_BOT = ty

    # --- Section 5: Monte Carlo Chart ---
    y = TAB_BOT - GAP_T
    section_title(pdf, PAD, y, "Revenue Distribution", font_size=13)
    y -= (GAP_B + 6)

    CHART_H = y - BODY_BOT
    pdf.setStrokeColor(GRAY_LINE)
    pdf.setLineWidth(0.5)
    pdf.roundRect(PAD - 4, BODY_BOT, INNER_W + 8, CHART_H + 2, 4, stroke=1, fill=0)
    try:
        pdf.drawImage(CHART_PATH, PAD + 2, BODY_BOT + 4,
                      width=INNER_W - 4, height=CHART_H - 6,
                      preserveAspectRatio=True)
    except Exception:
        pdf.setFillColor(GRAY_TEXT)
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(width / 2, BODY_BOT + CHART_H / 2,
                              "[Chart not found — save the chart before generating the PDF]")

    # --- CTA ---
    h_line(pdf, PAD, FOOTER_H + CTA_H, INNER_W, GRAY_LINE)
    pdf.setFillColor(DARK_BLUE)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawCentredString(width / 2, FOOTER_H + CTA_H - 22, "Unlock Your Revenue Potential")
    pdf.setFillColor(GRAY_TEXT)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, FOOTER_H + CTA_H - 40,
        "Hotels with stronger visibility and review engagement consistently outperform their competitors.")

    # --- Footer ---
    fill_rect(pdf, 0, 0, width, FOOTER_H, DARK_BLUE)
    fill_rect(pdf, 0, FOOTER_H, width, 3, TURQUOISE)
    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(width / 2, FOOTER_H - 24,
        "Your revenue growth starts today — don't let the competition get ahead.")
    pdf.setFillColor(ACCENT)
    pdf.setFont("Helvetica", 9)
    pdf.drawCentredString(width / 2, FOOTER_H - 44,
        "Ready to take the next step? Reach out and let's make it happen.")
    pdf.setFillColor(WHITE)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(width / 2, FOOTER_H - 64,
        f"customeralliance.com  ·  {SALES_NAME}  ·  {SALES_EMAIL}")

    # --- Save ---
    pdf.save()
    print(f"\n✅ Report saved: {PDF_PATH}")


# =============================================================================
# DOWNLOAD BUTTON (Google Colab)
# =============================================================================

def show_download_button():
    btn = widgets.Button(
        description="⬇️  Download PDF",
        button_style="primary",
        layout=widgets.Layout(width="200px", height="40px")
    )
    btn.on_click(lambda _: files.download(PDF_PATH))
    display(btn)


# =============================================================================
# MAIN
# =============================================================================

def main():

    # --- User inputs ---
    hotel_name = input("Enter hotel name: ")
    website    = input("Enter hotel website: ")
    rooms      = int(input("Enter the number of rooms: "))
    adr        = float(input("Enter the Average Daily Rate (€): "))
    occupancy  = float(input("Enter the occupancy level (e.g. 0.75): "))

    # --- Current revenue baseline ---
    current_revenue = rooms * adr * occupancy * 365

    # --- API call (disabled) ---
    # ai_visibility = get_ai_visibility(hotel_name, website)
    # print("\nAI Visibility Score:", ai_visibility)

    # --- Monte Carlo simulation ---
    simulated_revenue, percentiles = run_monte_carlo(rooms, adr, occupancy)

    # --- Chart ---
    drive.mount("/content/drive")
    plot_simulation(hotel_name, current_revenue, simulated_revenue, percentiles)

    # --- PDF report ---
    generate_pdf(
        hotel_name, website,
        rooms, adr, occupancy,
        current_revenue, percentiles
    )

    # --- Download button ---
    show_download_button()


if __name__ == "__main__":
    main()

# the end