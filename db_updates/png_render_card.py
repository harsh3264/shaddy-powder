# png_render_card.py
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ========== CONFIG ==========
SHOW_PLAYER_PHOTOS = True
DATAPITCH_LOGO_URL = "https://datapitch-assets.s3.eu-north-1.amazonaws.com/DataPitch.png"

BASE_W, BASE_H = 1080, 1080
SCALE = 2
W, H = BASE_W * SCALE, BASE_H * SCALE

# Colors
BG         = (10, 16, 28)
CARD_BG    = (17, 26, 44)
INNER_BG   = (22, 34, 56)
BORDER     = (40, 56, 86)
DIVIDER    = (44, 62, 96)
TEXT       = (242, 246, 252)
TEXT_SUB   = (184, 194, 208)

HEAD_YELLS = (248, 206, 54)
HEAD_FOULS = (232, 76, 76)
HEAD_SHOTS = (64, 182, 110)
RING_COL   = (120, 150, 255)

# ========== NETWORK ==========
def _session():
    s = requests.Session()
    retries = Retry(
        total=4, backoff_factor=0.4,
        status_forcelist=(429,500,502,503,504),
        allowed_methods=frozenset(["GET"])
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({
        "User-Agent":"Mozilla/5.0 (compatible; DataPitchBot/2.4)",
        "Referer":"https://api-sports.io"
    })
    return s

SESSION = _session()

def _retry_host(url: str) -> list:
    u = (url or "").strip()
    if not u:
        return []
    if "media-" in u and ".api-sports.io" in u:
        hosts = ["media-1.","media-2.","media-3.","media-4.","media."]
        out = []
        for h in hosts:
            out.append(u.replace("media-1.",h).replace("media-2.",h).replace("media-3.",h).replace("media-4.",h))
        dedup = []
        seen = set()
        for v in out:
            if v not in seen:
                dedup.append(v); seen.add(v)
        return dedup
    return [u]

def load_img(url, size=(100,100), circle=False):
    if not url:
        return Image.new("RGBA", size, (0,0,0,0))
    for u in _retry_host(url):
        try:
            r = SESSION.get(u, timeout=12, allow_redirects=True)
            if r.status_code != 200:
                continue
            im = Image.open(BytesIO(r.content)).convert("RGBA")
            im = ImageOps.contain(im, size, Image.Resampling.LANCZOS)
            if circle:
                m = Image.new("L", im.size, 0)
                ImageDraw.Draw(m).ellipse((0,0,im.size[0],im.size[1]), fill=255)
                im.putalpha(m)
            return im
        except Exception:
            continue
    return Image.new("RGBA", size, (0,0,0,0))

# ========== TEXT HELPERS ==========
def text_fit(draw, text, font, max_width):
    s = text if isinstance(text, str) else str(text or "")
    if draw.textbbox((0,0), s, font=font)[2] <= max_width:
        return s
    lo, hi = 1, len(s)
    while lo < hi:
        mid = (lo + hi)//2
        t = s[:mid] + "…"
        if draw.textbbox((0,0), t, font=font)[2] <= max_width:
            lo = mid + 1
        else:
            hi = mid
    return s[:max(1, lo-1)] + "…"

def split_name(name: str):
    s = (name if isinstance(name,str) else str(name or "")).strip()
    if not s: return "", ""
    parts = s.split()
    if len(parts) == 1: return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]

def smart_player_label(draw, name, pos, font, max_width):
    firsts, last = split_name(name)
    base = f"{name} ({pos})" if pos and str(pos).lower() not in ("na","none") else name
    if draw.textbbox((0,0), base, font=font)[2] <= max_width:
        return base
    if last:
        initial = (firsts[:1] + ". ").upper() if firsts else ""
        alt = f"{initial}{last} ({pos})" if pos and str(pos).lower() not in ("na","none") else f"{initial}{last}"
        if draw.textbbox((0,0), alt, font=font)[2] <= max_width:
            return alt
        return text_fit(draw, alt, font, max_width)
    return text_fit(draw, base, font, max_width)

def team_tag3(name: str):
    s = (name if isinstance(name,str) else str(name or "")).strip().upper()
    if not s: return ""
    parts = [p for p in s.split() if p]
    if len(parts) == 1: return parts[0][:3]
    return parts[-1][:3]

def format_last5(metric_val):
    if metric_val is None: return "—"
    s = str(metric_val).strip().replace("-", "")
    s = "".join(ch for ch in s if ch.isdigit())
    if not s: return "—"
    s = s[-5:]
    return "-".join(list(s))

# ========== DRAW HELPERS ==========
def draw_halo_badge(base, img, xy, halo_radius=10, pad=8):
    x, y = xy
    w, h = img.size
    halo = Image.new("RGBA", (w + pad*2, h + pad*2), (0,0,0,0))
    g = ImageDraw.Draw(halo)
    g.ellipse((0,0, halo.size[0]-1, halo.size[1]-1), fill=(255,255,255,80))
    halo = halo.filter(ImageFilter.GaussianBlur(halo_radius))
    base.alpha_composite(halo, (x - pad, y - pad))
    base.alpha_composite(img, (x, y))

def draw_headshot(base, center_xy, photo_url, ring_color, diameter_px):
    d = int(diameter_px * SCALE)
    ring_w = max(2*SCALE, int(0.06 * d))
    head = load_img(photo_url, size=(d, d), circle=True)
    x, y = center_xy
    halo = Image.new("RGBA", (d + 12*SCALE, d + 12*SCALE), (0,0,0,0))
    ImageDraw.Draw(halo).ellipse((0,0, halo.size[0]-1, halo.size[1]-1), fill=(255,255,255,70))
    halo = halo.filter(ImageFilter.GaussianBlur(6*SCALE))
    base.alpha_composite(halo, (x - halo.size[0]//2, y - halo.size[1]//2))
    ring2 = Image.new("RGBA", (d + 4*ring_w, d + 4*ring_w), (0,0,0,0))
    ImageDraw.Draw(ring2).ellipse((0,0, ring2.size[0]-1, ring2.size[1]-1), fill=ring_color + (220,))
    base.alpha_composite(ring2, (x - ring2.size[0]//2, y - ring2.size[1]//2))
    base.alpha_composite(head, (x - head.size[0]//2, y - head.size[1]//2))

def pill(draw, xy, text, font, fill, text_fill=(0,0,0)):
    x, y = xy
    pad_x, pad_y = 14*SCALE, 8*SCALE
    tw = draw.textbbox((0,0), text, font=font)[2]
    th = draw.textbbox((0,0), "Ay", font=font)[3]
    w = tw + pad_x*2
    h = th + pad_y*2
    draw.rounded_rectangle((x, y, x+w, y+h), radius=int(h*0.5), fill=fill)
    draw.text((x+pad_x, y+pad_y//2), text, font=font, fill=text_fill)
    return w, h

# ========== RENDER ==========
def render_stat_pack(data, out_path):
    canvas = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(canvas)

    # Fonts
    FONT_TTL  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 74)
    FONT_META = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    FONT_HEAD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
    FONT_NAME = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
    FONT_SUB  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
    FONT_TAG  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    FONT_MIC  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    FONT_FOOT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)

    SAFE = 64*SCALE
    CUR_Y = SAFE

    # Top row: League logo + Home/Away logos + Fixture title
    league_logo = load_img(data.get("league_logo"), (120, 120))
    draw_halo_badge(canvas, league_logo, (SAFE, CUR_Y), halo_radius=12*SCALE, pad=10*SCALE)
    
    home_logo = load_img(data["home_team"].get("logo"), (110, 110))
    away_logo = load_img(data["away_team"].get("logo"), (110, 110))
    
    # Position logos
    home_x = SAFE + 160*SCALE
    away_x = W - SAFE - 110*SCALE
    logo_y = CUR_Y
    
    # Draw logos with halo
    draw_halo_badge(canvas, home_logo, (home_x, logo_y), halo_radius=10*SCALE, pad=10*SCALE)
    draw_halo_badge(canvas, away_logo, (away_x, logo_y), halo_radius=10*SCALE, pad=10*SCALE)
    
    # Fixture text in the middle
    title_text = f"{data['home_team']['name']} vs {data['away_team']['name']}"
    tw = draw.textbbox((0,0), title_text, font=FONT_TTL)[2]
    text_x = (W - tw) // 2
    draw.text((text_x, CUR_Y + 25), title_text, font=FONT_TTL, fill=TEXT)
    
    CUR_Y += 140


    # Referee row
    ref = data.get("referee", {}) or {}
    ref_name = (ref.get("name") or "").strip()
    avg = ref.get("avg_yellows")
    try:
        avg = float(avg) if avg is not None else None
    except Exception:
        avg = None
    last5 = ref.get("last5")
    last5_fmt = str(last5).replace("|", " | ") if last5 else None

    ref_line = f"Ref: {ref_name}" if ref_name else "Ref: TBC"
    if avg is not None:
        ref_line += f" • Avg YC {round(avg,1)}"
    if last5_fmt:
        ref_line += f" • Last 5 YC: {last5_fmt}"

    ref_box = (SAFE, CUR_Y, W - SAFE, CUR_Y + 80*SCALE)
    draw.rounded_rectangle(ref_box, 20, fill=CARD_BG, outline=BORDER, width=2)
    draw.text((SAFE + 24*SCALE, CUR_Y + 24*SCALE), ref_line, font=FONT_META, fill=TEXT_SUB)
    CUR_Y += 90*SCALE

    # Top Yellow Bets
    header_h = 70
    draw.rounded_rectangle((SAFE, CUR_Y, W - SAFE, CUR_Y + header_h*SCALE), 22, fill=HEAD_YELLS)
    draw.text((SAFE + 26*SCALE, CUR_Y + 18*SCALE), "TOP YELLOW BETS", font=FONT_HEAD, fill=(20,20,24))
    CUR_Y += header_h*SCALE + 14*SCALE

    card_area = (SAFE, CUR_Y, W - SAFE, CUR_Y + 210*SCALE)
    draw.rounded_rectangle(card_area, 22, fill=INNER_BG, outline=BORDER, width=2)

    gap = 24*SCALE
    col_w = ((card_area[2] - card_area[0]) - 2*gap) // 3
    col_h = (card_area[3] - card_area[1])
    y_box_top = card_area[1]
    yellow_players = data["panels"]["yellows"][:3]

    for i in range(3):
        x0 = card_area[0] + i * (col_w + gap)
        x1 = x0 + col_w
        if i in (1, 2):
            draw.line((x0 - gap//2, y_box_top + 16*SCALE, x0 - gap//2, y_box_top + col_h - 16*SCALE),
                      fill=DIVIDER, width=1)
        if i < len(yellow_players):
            p = yellow_players[i]
            name = (p.get("name") or "").strip()
            pos  = (p.get("pos") or p.get("position") or "").strip()
            team = (p.get("team_name") or "").strip()
            l5   = p.get("metric")
            season_yc = p.get("season_league_cards")
            avg_fouls = p.get("avg_fouls_total")

            cx = x0 + 24*SCALE + 27*SCALE
            cy = y_box_top + 24*SCALE + 27*SCALE
            if SHOW_PLAYER_PHOTOS and p.get("photo"):
                draw_headshot(canvas, (cx, cy), p.get("photo"), RING_COL, diameter_px=54)

            text_x = cx + 27*SCALE + 16*SCALE
            label = smart_player_label(draw, name, pos, FONT_NAME, max_width=col_w - (text_x - x0) - 16*SCALE)
            draw.text((text_x, y_box_top + 22*SCALE), label, font=FONT_NAME, fill=TEXT)
            pill(draw, (text_x, y_box_top + 58*SCALE), team_tag3(team) or "—", FONT_TAG, (235,240,255), (20,24,32))

            l5s = l5 if isinstance(l5, str) else str(l5 or "—")
            draw.text((x0 + 24*SCALE, y_box_top + 108*SCALE), f"Season YC: {season_yc if season_yc is not None else '—'}",
                      font=FONT_MIC, fill=TEXT_SUB)
            draw.text((x0 + 24*SCALE, y_box_top + 142*SCALE), f"Avg Fouls: {avg_fouls if avg_fouls is not None else '—'}",
                      font=FONT_MIC, fill=TEXT_SUB)
            draw.text((x0 + 24*SCALE, y_box_top + 176*SCALE), f"Last 5 YC: {l5s}", font=FONT_MIC, fill=TEXT_SUB)

    CUR_Y = card_area[3] + 20*SCALE

    # Lower row
    lower_h = int(360 * SCALE)
    col_gap = 24*SCALE
    col_w2 = (W - SAFE*2 - col_gap) // 2
    left_box  = (SAFE, CUR_Y, SAFE + col_w2, CUR_Y + lower_h)
    right_box = (left_box[2] + col_gap, CUR_Y, left_box[2] + col_gap + col_w2, CUR_Y + lower_h)

    def header_bar(rect, color, title):
        x0, y0, x1, y1 = rect
        draw.rounded_rectangle(rect, 28, fill=CARD_BG, outline=BORDER, width=2)
        h = 80*SCALE
        draw.rounded_rectangle((x0 + 20*SCALE, y0 + 18*SCALE, x1 - 20*SCALE, y0 + 18*SCALE + h//SCALE),
                               22, fill=color)
        draw.text((x0 + 46*SCALE, y0 + 18*SCALE + 24), title, font=FONT_HEAD, fill=(20,20,24))
        draw.text((x0 + 28*SCALE, y0 + 18*SCALE + h//SCALE + 10*SCALE), "Last 5 starts (most recent right)",
                  font=FONT_SUB, fill=TEXT_SUB)
        return y0 + 18*SCALE + h//SCALE + 40*SCALE

    left_inner_top  = header_bar(left_box,  HEAD_FOULS, "TOP FOULERS")
    right_inner_top = header_bar(right_box, HEAD_SHOTS, "TOP SHOOTERS")

    def draw_list(rect, players):
        x0, y0, x1, y1 = rect
        row_h = int(100*SCALE)
        photo_d = 50
        cur_y = y0
        for idx, p in enumerate(players[:5]):
            if idx > 0:
                draw.line((x0 + 12, cur_y - int(12*SCALE), x1 - 12, cur_y - int(12*SCALE)), fill=DIVIDER, width=1)
            name = (p.get("name") or "").strip()
            pos  = (p.get("pos") or p.get("position") or "").strip()
            team = (p.get("team_name") or "").strip()
            l5   = p.get("metric")

            cx = x0 + 20*SCALE + (photo_d//2) * SCALE
            cy = cur_y + row_h//2 - int(18*SCALE)
            if SHOW_PLAYER_PHOTOS and p.get("photo"):
                draw_headshot(canvas, (cx, cy), p.get("photo"), RING_COL, photo_d)

            text_x = cx + (photo_d//2)*SCALE + 14*SCALE
            max_w  = (x1 - x0) - (text_x - x0) - 16*SCALE
            label  = smart_player_label(draw, name, pos, FONT_NAME, max_w)
            draw.text((text_x, cy - int(32*SCALE)), label, font=FONT_NAME, fill=TEXT)
            draw.text((text_x, cy + int(6*SCALE)), f"{l5}", font=FONT_SUB, fill=TEXT_SUB)
            pill(draw, (text_x, cy + int(38*SCALE)), team_tag3(team) or "—", FONT_TAG, (235,240,255), (20,24,32))
            cur_y += row_h

    draw_list((left_box[0] + 18*SCALE, left_inner_top, left_box[2] - 18*SCALE, left_box[3] - 18*SCALE),
              data["panels"]["fouls"])
    draw_list((right_box[0] + 18*SCALE, right_inner_top, right_box[2] - 18*SCALE, right_box[3] - 18*SCALE),
              data["panels"]["shots"])

    # Footer
    dp_logo = load_img(DATAPITCH_LOGO_URL, size=(110, 110))
    lx = (W - dp_logo.size[0]) // 2
    ly = H - dp_logo.size[1] - 24*SCALE  # bottom aligned
    canvas.alpha_composite(dp_logo, (lx, ly))

    strap = "Powered by DataPitch  •  18+ Gamble Responsibly"
    sw = draw.textbbox((0,0), strap, font=FONT_FOOT)[2]
    draw.text(((W - sw)//2, ly - 36*SCALE), strap, font=FONT_FOOT, fill=TEXT_SUB)

    final = canvas.resize((BASE_W, BASE_H), resample=Image.Resampling.LANCZOS)
    final = final.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=3))
    final.convert("RGB").save(out_path, quality=95)
    return out_path
