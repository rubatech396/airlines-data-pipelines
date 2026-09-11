

import tkinter as tk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


# ============================================================
# 1. LOAD DATA
# ============================================================

folder = "/Users/rubasri/Downloads/UseCase - Airlines 1"
file_path = os.path.join(folder, "cleaned_airlines.csv")

try:
    df = pd.read_csv(file_path)
except Exception as e:
    messagebox.showerror(
        "Error",
        "Could not load cleaned_airlines.csv\n\n" + str(e)
    )
    raise


# ============================================================
# 2. CLEAN DATA
# ============================================================

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
).fillna(0)

df["status"] = (
    df["status"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df["airline"] = (
    df["airline"]
    .astype(str)
    .str.strip()
)

df["payment_method"] = (
    df["payment_method"]
    .astype(str)
    .str.strip()
)


# ============================================================
# 3. KPI CALCULATIONS
# ============================================================

total_bookings = df["booking_id"].nunique()

confirmed = (
    df["status"] == "CONFIRMED"
).sum()

cancelled = (
    df["status"] == "CANCELLED"
).sum()

pending = (
    df["status"] == "PENDING"
).sum()

total_passengers = df["passenger_id"].nunique()

total_revenue = df["amount"].sum()


# ============================================================
# 4. MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("Airlines Analytics Dashboard")

root.geometry("1100x700")

root.minsize(900, 600)

root.configure(
    bg="#F4F6F8"
)


# ============================================================
# 5. SIDEBAR
# ============================================================

sidebar = tk.Frame(
    root,
    bg="#172033",
    width=190
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


# Logo / Title

logo = tk.Label(
    sidebar,
    text="✈ AIRLINES",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#172033"
)

logo.pack(
    pady=(30, 35)
)


# Sidebar menu

menu_items = [
    "Dashboard",
    "Bookings",
    "Passengers",
    "Flights",
    "Payments"
]


for item in menu_items:

    menu = tk.Label(
        sidebar,
        text="  " + item,
        font=("Arial", 11),
        anchor="w",
        padx=20,
        pady=12,
        fg="white",
        bg="#172033"
    )

    menu.pack(
        fill="x"
    )


# ============================================================
# 6. MAIN CONTENT
# ============================================================

main = tk.Frame(
    root,
    bg="#F4F6F8"
)

main.pack(
    side="left",
    fill="both",
    expand=True
)


# ============================================================
# 7. HEADER
# ============================================================

header = tk.Frame(
    main,
    bg="#F4F6F8"
)

header.pack(
    fill="x",
    padx=25,
    pady=(20, 5)
)


title = tk.Label(
    header,
    text="Airlines Analytics",
    font=("Arial", 22, "bold"),
    fg="#172033",
    bg="#F4F6F8"
)

title.pack(
    side="left"
)


date_label = tk.Label(
    header,
    text="Booking & Revenue Overview",
    font=("Arial", 10),
    fg="#667085",
    bg="#F4F6F8"
)

date_label.pack(
    side="right",
    pady=8
)


# ============================================================
# 8. KPI CARDS
# ============================================================

kpi_frame = tk.Frame(
    main,
    bg="#F4F6F8"
)

kpi_frame.pack(
    fill="x",
    padx=25,
    pady=15
)


kpis = [
    ("TOTAL BOOKINGS", total_bookings),
    ("CONFIRMED", confirmed),
    ("CANCELLED", cancelled),
    ("PASSENGERS", total_passengers),
    ("REVENUE", "₹" + format(total_revenue, ",.0f"))
]


for i, (label, value) in enumerate(kpis):

    card = tk.Frame(
        kpi_frame,
        bg="white",
        highlightbackground="#E4E7EC",
        highlightthickness=1
    )

    card.grid(
        row=0,
        column=i,
        padx=5,
        sticky="nsew"
    )

    kpi_frame.columnconfigure(
        i,
        weight=1
    )

    label_widget = tk.Label(
        card,
        text=label,
        font=("Arial", 8, "bold"),
        fg="#667085",
        bg="white"
    )

    label_widget.pack(
        anchor="w",
        padx=12,
        pady=(12, 3)
    )

    value_widget = tk.Label(
        card,
        text=str(value),
        font=("Arial", 16, "bold"),
        fg="#172033",
        bg="white"
    )

    value_widget.pack(
        anchor="w",
        padx=12,
        pady=(0, 12)
    )


# ============================================================
# 9. CHART AREA
# ============================================================

chart_container = tk.Frame(
    main,
    bg="#F4F6F8"
)

chart_container.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=5
)


# ============================================================
# 10. MATPLOTLIB FIGURE
# ============================================================

fig, axes = plt.subplots(
    2,
    2,
    figsize=(9, 5.5)
)

fig.patch.set_facecolor("#F4F6F8")


# ============================================================
# CHART 1
# BOOKINGS BY AIRLINE
# ============================================================

airline_bookings = (
    df.groupby("airline")["booking_id"]
    .nunique()
    .sort_values(ascending=False)
)


axes[0, 0].bar(
    airline_bookings.index,
    airline_bookings.values
)

axes[0, 0].set_title(
    "Bookings by Airline",
    fontsize=11,
    fontweight="bold",
    loc="left"
)

axes[0, 0].set_ylabel(
    "Bookings",
    fontsize=8
)

axes[0, 0].tick_params(
    axis="x",
    labelsize=7,
    rotation=30
)

axes[0, 0].tick_params(
    axis="y",
    labelsize=7
)




# ============================================================
# CHART 2 - BOOKING STATUS MEDIUM DONUT
# ============================================================

status = (
    df["status"]
    .astype(str)
    .str.strip()
    .str.upper()
    .value_counts()
)

# Medium donut - no labels inside the slices
wedges, texts, autotexts = axes[0, 1].pie(
    status.values,
    autopct="%1.1f%%",
    startangle=90,
    radius=0.72,
    pctdistance=0.72,
    wedgeprops={
        "width": 0.35,
        "edgecolor": "white"
    },
    textprops={
        "fontsize": 8,
        "fontweight": "bold"
    }
)

# Percentage text
for text in autotexts:
    text.set_fontsize(4)
    text.set_fontweight("bold")

# ALL status names shown clearly in legend
axes[0, 1].legend(
    wedges,
    status.index,
    title="Status",
    loc="center left",
    bbox_to_anchor=(0.95, 0.5),
    fontsize=8,
    title_fontsize=9,
    frameon=False
)

axes[0, 1].set_title(
    "Booking Status",
    fontsize=11,
    fontweight="bold",
    loc="left"
)

axes[0, 1].axis("equal")






# ============================================================
# CHART 3
# REVENUE BY AIRLINE
# ============================================================

airline_revenue = (
    df.groupby("airline")["amount"]
    .sum()
    .sort_values(ascending=False)
)


axes[1, 0].bar(
    airline_revenue.index,
    airline_revenue.values
)

axes[1, 0].set_title(
    "Revenue by Airline",
    fontsize=11,
    fontweight="bold",
    loc="left"
)

axes[1, 0].set_ylabel(
    "Revenue",
    fontsize=8
)

axes[1, 0].tick_params(
    axis="x",
    labelsize=7,
    rotation=30
)

axes[1, 0].tick_params(
    axis="y",
    labelsize=7
)


# ============================================================
# CHART 4
# PAYMENT METHODS
# ============================================================

payment_methods = (
    df["payment_method"]
    .value_counts()
)


axes[1, 1].bar(
    payment_methods.index,
    payment_methods.values
)

axes[1, 1].set_title(
    "Payment Methods",
    fontsize=11,
    fontweight="bold",
    loc="left"
)

axes[1, 1].set_ylabel(
    "Payments",
    fontsize=8
)

axes[1, 1].tick_params(
    axis="x",
    labelsize=7,
    rotation=30
)

axes[1, 1].tick_params(
    axis="y",
    labelsize=7
)


# ============================================================
# 11. CLEAN CHART APPEARANCE
# ============================================================

for ax in axes.flat:

    ax.set_facecolor("white")

    ax.spines["top"].set_visible(False)

    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_color("#DDDDDD")

    ax.spines["bottom"].set_color("#DDDDDD")

    ax.grid(
        axis="y",
        alpha=0.15
    )


fig.tight_layout(
    pad=2
)


# ============================================================
# 12. DISPLAY CHART
# ============================================================

canvas = FigureCanvasTkAgg(
    fig,
    master=chart_container
)

canvas.draw()

canvas.get_tk_widget().pack(
    fill="both",
    expand=True
)


# ============================================================
# 13. FOOTER
# ============================================================

footer = tk.Label(
    main,
    text="Airlines Data Pipeline • Cleaned and analyzed using Python",
    font=("Arial", 8),
    fg="#667085",
    bg="#F4F6F8"
)

footer.pack(
    pady=(0, 8)
)


# ============================================================
# 14. RUN
# ============================================================

root.mainloop()



