"""Generate two PNG diagrams for the Stateless Session Management portfolio item.

Outputs:
  ../assets/sessions_webfarm.png
  ../assets/sessions_design.png

Style intentionally matches the simple draw.io look of the other portfolio assets:
light-gray fills, thin black borders, sans-serif labels, a yellow callout for the key idea.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

FILL = "#f4f4f4"
BORDER = "#333333"
CALLOUT_FILL = "#fff8c4"
CALLOUT_BORDER = "#c9b500"
ACCENT = "#2b6cb0"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
})


def rounded_box(ax, x, y, w, h, text, fill=FILL, border=BORDER, fontsize=11, weight="normal"):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2, edgecolor=border, facecolor=fill,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, color=BORDER, lw=1.2, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                  mutation_scale=14, linewidth=lw, color=color))


# ---------- Diagram 1: web farm with session state in SQL ----------
fig, ax = plt.subplots(figsize=(8, 7.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect("equal")
ax.axis("off")

# Users
rounded_box(ax, 3.5, 8.8, 3, 0.8, "Users (browsers)")

# Load balancer
rounded_box(ax, 3.5, 7.2, 3, 0.8, "Load Balancer")

# Two web servers
rounded_box(ax, 1.0, 5.0, 3, 1.4, "Web Server A\n(IIS / ASP Classic)")
rounded_box(ax, 6.0, 5.0, 3, 1.4, "Web Server B\n(IIS / ASP Classic)")

# Session state DB
rounded_box(ax, 3.0, 2.0, 4, 1.4, "SQL Server\nShared Session State", fill="#e6f0fa", border=ACCENT, weight="bold")

# Arrows
arrow(ax, 5.0, 8.78, 5.0, 8.02)              # users -> LB
arrow(ax, 4.4, 7.18, 2.7, 6.42)              # LB -> A
arrow(ax, 5.6, 7.18, 7.3, 6.42)              # LB -> B
arrow(ax, 2.5, 4.98, 4.0, 3.42)              # A -> DB
arrow(ax, 7.5, 4.98, 6.0, 3.42)              # B -> DB
arrow(ax, 4.0, 3.42, 2.5, 4.98, color=ACCENT)   # DB -> A (return)
arrow(ax, 6.0, 3.42, 7.5, 4.98, color=ACCENT)   # DB -> B (return)

# Callout
callout = FancyBboxPatch(
    (0.2, 0.3), 9.6, 1.0,
    boxstyle="round,pad=0.02,rounding_size=0.06",
    linewidth=1.2, edgecolor=CALLOUT_BORDER, facecolor=CALLOUT_FILL,
)
ax.add_patch(callout)
ax.text(5.0, 0.8,
        "Session state lives in the database, not in either server's memory.\n"
        "Either web server can serve any user. App pool recycles become invisible.",
        ha="center", va="center", fontsize=11)

ax.set_title("Stateless Session Management for ASP Classic on IIS", fontsize=13, weight="bold", pad=8)

fig.tight_layout()
fig.savefig(ASSETS / "sessions_webfarm.png", dpi=160, bbox_inches="tight", facecolor="white")
plt.close(fig)


# ---------- Diagram 2: side-by-side provider/manager/repository ----------
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 9)
ax.set_aspect("equal")
ax.axis("off")

# Column titles
ax.text(3.0, 8.4, "ASP.NET (Microsoft, MIT-licensed)\nAspNetSessionState v2.0.0",
        ha="center", va="center", fontsize=12, weight="bold")
ax.text(9.0, 8.4, "ASP Classic (our implementation)\nElab Session Abstraction",
        ha="center", va="center", fontsize=12, weight="bold")

# Vertical divider
ax.plot([6.0, 6.0], [0.6, 7.7], color="#bbbbbb", linestyle="--", linewidth=1.0)

# Left column boxes
rounded_box(ax, 1.5, 6.2, 3, 0.9, "SessionStateProvider", weight="bold")
rounded_box(ax, 0.2, 4.4, 2.2, 0.9, "SessionStateStore")
rounded_box(ax, 3.7, 4.4, 2.2, 0.9, "SessionStateRepository")
rounded_box(ax, 1.95, 2.6, 2.1, 0.9, "SessionManager")
rounded_box(ax, 1.5, 0.8, 3, 0.9, "SQL Server tables\n(ASP.NET schema)", fill="#e6f0fa", border=ACCENT)

# Left arrows
arrow(ax, 2.0, 6.18, 1.3, 5.32)
arrow(ax, 4.0, 6.18, 4.8, 5.32)
arrow(ax, 3.0, 6.18, 3.0, 3.52)
arrow(ax, 4.8, 4.38, 3.0, 1.72)

# Right column boxes (mirror layout, intentionally identical shape)
rounded_box(ax, 7.5, 6.2, 3, 0.9, "SqlSessionStateProvider", weight="bold")
rounded_box(ax, 6.2, 4.4, 2.2, 0.9, "SqlSessionStore")
rounded_box(ax, 9.7, 4.4, 2.2, 0.9, "SqlSessionStateRepository")
rounded_box(ax, 7.95, 2.6, 2.1, 0.9, "ElabSessionManager")
rounded_box(ax, 7.5, 0.8, 3, 0.9, "SQL Server tables\n(same schema, JSON payload)", fill="#e6f0fa", border=ACCENT)

# Right arrows
arrow(ax, 8.0, 6.18, 7.3, 5.32)
arrow(ax, 10.0, 6.18, 10.8, 5.32)
arrow(ax, 9.0, 6.18, 9.0, 3.52)
arrow(ax, 10.8, 4.38, 9.0, 1.72)

# Callout
callout = FancyBboxPatch(
    (0.2, -0.1), 11.6, 0.7,
    boxstyle="round,pad=0.02,rounding_size=0.06",
    linewidth=1.2, edgecolor=CALLOUT_BORDER, facecolor=CALLOUT_FILL,
)
ax.add_patch(callout)
ax.text(6.0, 0.25,
        "Same shapes on purpose. An engineer who knows the modern framework recognizes the older one.",
        ha="center", va="center", fontsize=11)

ax.set_title("Borrowing a Microsoft Pattern to Mend an Older Microsoft Stack",
             fontsize=13, weight="bold", pad=8)

fig.tight_layout()
fig.savefig(ASSETS / "sessions_design.png", dpi=160, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(f"Wrote {ASSETS / 'sessions_webfarm.png'}")
print(f"Wrote {ASSETS / 'sessions_design.png'}")
