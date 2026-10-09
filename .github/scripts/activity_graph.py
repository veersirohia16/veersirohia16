"""Generate a themed contribution activity line graph (last 31 days) as SVG."""
import json
import os
import sys
import urllib.request
from datetime import date, timedelta

USER = os.environ.get("USERNAME", "veersirohia16")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.environ.get("OUT", "profile-activity/activity-graph.svg")
DAYS = 31


def fetch():
    """Read the public contribution calendar (includes private counts when enabled)."""
    import re
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"User-Agent": "profile-activity-graph"})
    html = urllib.request.urlopen(req).read().decode()
    tips = {m.group(1): m.group(2) for m in re.finditer(
        r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html)}
    days = []
    for m in re.finditer(r'<td[^>]*data-date="([0-9-]+)"[^>]*>', html):
        td = m.group(0)
        idm = re.search(r'id="([^"]+)"', td)
        tip = tips.get(idm.group(1), "") if idm else ""
        num = re.match(r"\s*(\d+)", tip)
        days.append((m.group(1), int(num.group(1)) if num else 0))
    days.sort()
    today = str(date.today())
    days = [d for d in days if d[0] <= today]
    return days[-DAYS:]


def render(days):
    W, H = 900, 300
    L, R, T, B = 60, 30, 50, 50
    pw, ph = W - L - R, H - T - B
    vals = [c for _, c in days]
    mx = max(-(-max(vals) // 4) * 4, 4)
    n = len(days)
    xs = [L + i * pw / max(n - 1, 1) for i in range(n)]
    ys = [T + ph - v / mx * ph for v in vals]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    area = f"{L},{T+ph} " + pts + f" {xs[-1]:.1f},{T+ph}"
    bg, fg, line, accent, grid = "#1a1b27", "#70a5fd", "#bf91f3", "#38bdae", "#2a2c3d"
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{line}" stop-opacity="0.45"/>'
         f'<stop offset="1" stop-color="{line}" stop-opacity="0"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="8" fill="{bg}"/>',
         f'<text x="{W/2}" y="30" fill="{fg}" font-family="Segoe UI,Ubuntu,sans-serif" '
         f'font-size="18" font-weight="600" text-anchor="middle">{USER}\'s Contribution Graph</text>']
    for k in range(5):
        v = mx * k / 4
        y = T + ph - ph * k / 4
        o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{grid}" stroke-dasharray="3 4"/>')
        o.append(f'<text x="{L-10}" y="{y+4:.1f}" fill="{fg}" font-family="Segoe UI,Ubuntu,sans-serif" '
                 f'font-size="11" text-anchor="end">{v:.0f}</text>')
    o.append(f'<polygon points="{area}" fill="url(#g)"/>')
    o.append(f'<polyline points="{pts}" fill="none" stroke="{line}" stroke-width="2.5" '
             'stroke-linejoin="round" stroke-linecap="round"/>')
    for i, ((d, v), x, y) in enumerate(zip(days, xs, ys)):
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{accent}"><title>{d}: {v}</title></circle>')
        if i % 5 == 0 or i == n - 1:
            o.append(f'<text x="{x:.1f}" y="{H-B+20}" fill="{fg}" font-family="Segoe UI,Ubuntu,sans-serif" '
                     f'font-size="11" text-anchor="middle">{d[5:]}</text>')
    o.append(f'<text x="{W/2}" y="{H-8}" fill="{fg}" font-family="Segoe UI,Ubuntu,sans-serif" '
             'font-size="12" text-anchor="middle" opacity="0.8">Days (last 31)</text>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    days = fetch() if len(sys.argv) < 2 else json.load(open(sys.argv[1]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write(render(days))
    print(f"wrote {OUT} ({len(days)} days)")
