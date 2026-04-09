from __future__ import annotations

import base64
from pathlib import Path
import time
from dataclasses import asdict
from typing import Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components

from tarot.logic import DrawnCard, SpreadType, draw_spread, load_cards, spread_positions


def _init_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "reveal" not in st.session_state:
        st.session_state.reveal = []
    if "latest_ts" not in st.session_state:
        st.session_state.latest_ts = None


def _asset_data_uri(rel_path: str) -> str:
    p = Path(__file__).parent / rel_path
    raw = p.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    ext = p.suffix.lower()
    mime = "image/svg+xml" if ext == ".svg" else "application/octet-stream"
    return f"data:{mime};base64,{b64}"


def _svg_data_uri(svg: str) -> str:
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def _card_illustration_uri(card_id: str) -> str:
    """
    Small cartoon-ish SVG illustration per Major Arcana id (00-21).
    No external assets; deterministic and lightweight.
    """
    bg_by_id = {
        "00": ("#FF6B6B", "#FFD93D"),  # Fool
        "01": ("#7C3AED", "#22D3EE"),  # Magician
        "02": ("#111827", "#A78BFA"),  # High Priestess
        "03": ("#16A34A", "#FDE68A"),  # Empress
        "04": ("#0EA5E9", "#1F2937"),  # Emperor
        "05": ("#F59E0B", "#111827"),  # Hierophant
        "06": ("#FB7185", "#60A5FA"),  # Lovers
        "07": ("#22C55E", "#0EA5E9"),  # Chariot
        "08": ("#F97316", "#FDE047"),  # Strength
        "09": ("#0F172A", "#93C5FD"),  # Hermit
        "10": ("#22D3EE", "#A78BFA"),  # Wheel
        "11": ("#94A3B8", "#FBBF24"),  # Justice
        "12": ("#38BDF8", "#FB7185"),  # Hanged Man
        "13": ("#111827", "#6B7280"),  # Death
        "14": ("#34D399", "#60A5FA"),  # Temperance
        "15": ("#EF4444", "#111827"),  # Devil
        "16": ("#F97316", "#7C3AED"),  # Tower
        "17": ("#60A5FA", "#A78BFA"),  # Star
        "18": ("#0B1020", "#4DD0FF"),  # Moon
        "19": ("#FDE047", "#FB7185"),  # Sun
        "20": ("#A78BFA", "#FDE047"),  # Judgement
        "21": ("#22C55E", "#A78BFA"),  # World
    }
    a, b = bg_by_id.get(card_id, ("#64748B", "#22D3EE"))

    # Simple icon primitives by id
    icon = {
        "00": '<path d="M36 76c10-16 18-28 28-40 9-10 17-16 28-22" stroke="rgba(255,255,255,.92)" stroke-width="6" fill="none" stroke-linecap="round"/><circle cx="78" cy="34" r="10" fill="rgba(255,255,255,.9)"/>',
        "01": '<path d="M64 26v56" stroke="rgba(255,255,255,.92)" stroke-width="7" stroke-linecap="round"/><path d="M38 40h52" stroke="rgba(255,255,255,.86)" stroke-width="7" stroke-linecap="round"/><circle cx="64" cy="82" r="10" fill="rgba(255,255,255,.22)" stroke="rgba(255,255,255,.6)" stroke-width="3"/>',
        "02": '<path d="M38 78c10-18 38-18 52 0" fill="none" stroke="rgba(255,255,255,.88)" stroke-width="6" stroke-linecap="round"/><circle cx="64" cy="52" r="16" fill="rgba(255,255,255,.14)" stroke="rgba(255,255,255,.65)" stroke-width="3"/><circle cx="64" cy="52" r="5" fill="rgba(255,255,255,.9)"/>',
        "03": '<path d="M30 74c16 16 52 16 68 0" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="6" stroke-linecap="round"/><path d="M40 58c6-10 10-16 24-16s18 6 24 16" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="5" stroke-linecap="round"/>',
        "04": '<path d="M46 86V40" stroke="rgba(255,255,255,.92)" stroke-width="7" stroke-linecap="round"/><path d="M82 86V40" stroke="rgba(255,255,255,.92)" stroke-width="7" stroke-linecap="round"/><path d="M40 44h48" stroke="rgba(255,255,255,.75)" stroke-width="6" stroke-linecap="round"/>',
        "05": '<path d="M64 30l12 18-12 18-12-18z" fill="rgba(255,255,255,.22)" stroke="rgba(255,255,255,.75)" stroke-width="3"/><path d="M38 84h52" stroke="rgba(255,255,255,.86)" stroke-width="6" stroke-linecap="round"/>',
        "06": '<path d="M44 54c-8-10 4-26 20-18 16-8 28 8 20 18-5 6-11 10-20 18-9-8-15-12-20-18z" fill="rgba(255,255,255,.26)" stroke="rgba(255,255,255,.72)" stroke-width="3"/>',
        "07": '<path d="M40 78h48l-6-26H46z" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.7)" stroke-width="3"/><circle cx="52" cy="82" r="7" fill="rgba(255,255,255,.75)"/><circle cx="76" cy="82" r="7" fill="rgba(255,255,255,.75)"/>',
        "08": '<path d="M44 78c0-18 40-18 40 0" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="6" stroke-linecap="round"/><path d="M48 60c6-10 26-10 32 0" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="5" stroke-linecap="round"/>',
        "09": '<path d="M64 30v56" stroke="rgba(255,255,255,.92)" stroke-width="6" stroke-linecap="round"/><circle cx="64" cy="40" r="10" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.7)" stroke-width="3"/><path d="M58 92h12" stroke="rgba(255,255,255,.8)" stroke-width="6" stroke-linecap="round"/>',
        "10": '<circle cx="64" cy="60" r="22" fill="rgba(255,255,255,.16)" stroke="rgba(255,255,255,.72)" stroke-width="3"/><path d="M64 38v44M42 60h44" stroke="rgba(255,255,255,.78)" stroke-width="5" stroke-linecap="round"/>',
        "11": '<path d="M40 46h48" stroke="rgba(255,255,255,.86)" stroke-width="6" stroke-linecap="round"/><path d="M64 46v44" stroke="rgba(255,255,255,.86)" stroke-width="6" stroke-linecap="round"/><path d="M44 90h40" stroke="rgba(255,255,255,.5)" stroke-width="6" stroke-linecap="round"/>',
        "12": '<path d="M64 28v22" stroke="rgba(255,255,255,.86)" stroke-width="6" stroke-linecap="round"/><path d="M46 50h36" stroke="rgba(255,255,255,.86)" stroke-width="6" stroke-linecap="round"/><path d="M64 50v44" stroke="rgba(255,255,255,.5)" stroke-width="6" stroke-linecap="round"/>',
        "13": '<path d="M46 84c14-26 22-40 36-56" stroke="rgba(255,255,255,.88)" stroke-width="6" stroke-linecap="round"/><path d="M46 28l36 56" stroke="rgba(255,255,255,.4)" stroke-width="6" stroke-linecap="round"/>',
        "14": '<path d="M44 78c8-18 32-18 40 0" fill="none" stroke="rgba(255,255,255,.88)" stroke-width="6" stroke-linecap="round"/><path d="M44 46c8 18 32 18 40 0" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="6" stroke-linecap="round"/>',
        "15": '<path d="M50 44h28v28H50z" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.7)" stroke-width="3"/><path d="M42 84h44" stroke="rgba(255,255,255,.86)" stroke-width="6" stroke-linecap="round"/>',
        "16": '<path d="M44 86l20-52 20 52" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="6" stroke-linejoin="round"/><path d="M54 58h20" stroke="rgba(255,255,255,.55)" stroke-width="6" stroke-linecap="round"/>',
        "17": '<path d="M64 26l6 18h19l-15 11 6 18-16-11-16 11 6-18-15-11h19z" fill="rgba(255,255,255,.22)" stroke="rgba(255,255,255,.72)" stroke-width="3"/>',
        "18": '<path d="M48 70c8 12 24 12 32 0" fill="none" stroke="rgba(255,255,255,.8)" stroke-width="6" stroke-linecap="round"/><circle cx="52" cy="52" r="10" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.7)" stroke-width="3"/><circle cx="76" cy="52" r="10" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.7)" stroke-width="3"/>',
        "19": '<circle cx="64" cy="56" r="18" fill="rgba(255,255,255,.22)" stroke="rgba(255,255,255,.72)" stroke-width="3"/><path d="M64 26v12M64 74v12M34 56h12M82 56h12" stroke="rgba(255,255,255,.82)" stroke-width="5" stroke-linecap="round"/>',
        "20": '<path d="M40 80c8-18 40-18 48 0" fill="none" stroke="rgba(255,255,255,.88)" stroke-width="6" stroke-linecap="round"/><path d="M52 40h24l-12 18z" fill="rgba(255,255,255,.20)" stroke="rgba(255,255,255,.7)" stroke-width="3"/>',
        "21": '<circle cx="64" cy="58" r="24" fill="rgba(255,255,255,.16)" stroke="rgba(255,255,255,.72)" stroke-width="3"/><path d="M64 34c-10 10-10 36 0 48 10-12 10-36 0-48z" fill="rgba(255,255,255,.12)"/>',
    }.get(card_id, '<circle cx="64" cy="58" r="22" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.7)" stroke-width="3"/><path d="M52 58h24" stroke="rgba(255,255,255,.85)" stroke-width="6" stroke-linecap="round"/>')

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="180" height="140" viewBox="0 0 128 104">
      <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="{a}"/>
          <stop offset="1" stop-color="{b}"/>
        </linearGradient>
        <filter id="s" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="6"/>
        </filter>
      </defs>
      <rect x="0" y="0" width="128" height="104" rx="18" fill="url(#g)"/>
      <circle cx="22" cy="18" r="18" fill="rgba(255,255,255,.18)" filter="url(#s)"/>
      <circle cx="112" cy="92" r="22" fill="rgba(0,0,0,.16)" filter="url(#s)"/>
      <g transform="translate(0 2)">{icon}</g>
    </svg>
    """
    return _svg_data_uri(svg)


def _inject_theme() -> None:
    card_back = _asset_data_uri("assets/card_back.svg")
    st.markdown(
        f"""
        <style>
          :root {{
            /* Soft pastel theme (high clarity) */
            --bg0: #F7F5FF;
            --bg1: #F3F7FF;
            --panel: rgba(255,255,255,0.74);
            --panel2: rgba(255,255,255,0.92);
            --stroke: rgba(15, 23, 42, 0.10);
            --stroke2: rgba(15, 23, 42, 0.14);
            --text: rgba(15, 23, 42, 0.92);
            --muted: rgba(30, 41, 59, 0.72);
            --muted2: rgba(51, 65, 85, 0.60);
            --accentA: rgba(168, 85, 247, 0.10);
            --accentB: rgba(56, 189, 248, 0.10);
            --accentC: rgba(251, 191, 36, 0.08);
          }}

          /* App background + layout */
          .stApp {{
            background:
              radial-gradient(1200px 600px at 20% 10%, var(--accentA), rgba(0,0,0,0) 60%),
              radial-gradient(900px 700px at 80% 15%, var(--accentB), rgba(0,0,0,0) 55%),
              radial-gradient(900px 700px at 50% 110%, var(--accentC), rgba(0,0,0,0) 55%),
              linear-gradient(180deg, var(--bg0) 0%, var(--bg1) 60%, #FFFFFF 100%);
          }}

          /* Make default containers feel "premium" */
          section[data-testid="stSidebar"] > div {{
            background: var(--panel);
            border-right: 1px solid var(--stroke);
            backdrop-filter: blur(10px);
          }}

          /* unify widget rows */
          section[data-testid="stSidebar"] label,
          section[data-testid="stSidebar"] p,
          section[data-testid="stSidebar"] span {{
            color: var(--muted) !important;
          }}

          /* top header panel */
          .tg-header {{
            border: 1px solid var(--stroke);
            background: linear-gradient(180deg, var(--panel2), rgba(255,255,255,0.62));
            border-radius: 18px;
            padding: 16px 16px 14px 16px;
            box-shadow: 0 18px 50px rgba(15, 23, 42, 0.10);
            backdrop-filter: blur(10px);
          }}

          /* Tarot card component */
          .tarot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            align-items: start;
            justify-items: center;
          }}

          /* Prefer a single-row 3-card layout on wider screens */
          @media (min-width: 980px) {{
            .tarot-grid.three {{
              grid-template-columns: repeat(3, minmax(0, 1fr));
            }}
          }}

          .tarot-card {{
            position: relative;
            width: 100%;
            aspect-ratio: 7 / 11;
            border-radius: 16px;
            perspective: 1200px;
            max-width: 220px; /* prevents single-card being huge */
          }}

          .tarot-inner {{
            position: absolute;
            inset: 0;
            border-radius: 16px;
            transform-style: preserve-3d;
            transition: transform 720ms cubic-bezier(.2,.8,.2,1);
            box-shadow:
              0 18px 42px rgba(15, 23, 42, 0.14),
              0 1px 0 rgba(255,255,255,0.55) inset;
          }}

          .tarot-card.is-revealed .tarot-inner {{
            transform: rotateY(180deg);
          }}

          .tarot-face {{
            position: absolute;
            inset: 0;
            border-radius: 16px;
            backface-visibility: hidden;
            overflow: hidden;
          }}

          .tarot-back {{
            background-image: url("{card_back}");
            background-size: cover;
            background-position: center;
            filter: saturate(1.05) contrast(1.0);
          }}

          .tarot-front {{
            transform: rotateY(180deg);
            background:
              radial-gradient(900px 500px at 30% 10%, rgba(168,85,247,0.10), rgba(0,0,0,0) 60%),
              radial-gradient(900px 500px at 80% 10%, rgba(56,189,248,0.08), rgba(0,0,0,0) 55%),
              linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.76));
            border: 1px solid var(--stroke2);
          }}

          .tarot-front .ill {{
            width: 100%;
            height: 78px;
            border-radius: 12px;
            border: 1px solid var(--stroke);
            background-size: cover;
            background-position: center;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.12);
          }}

          .tarot-front .badge {{
            display: inline-block;
            font-size: 11px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
            background: rgba(15, 23, 42, 0.04);
            border: 1px solid var(--stroke);
            padding: 5px 9px;
            border-radius: 999px;
          }}

          .tarot-front .title {{
            margin-top: 12px;
            font-size: 16px;
            font-weight: 760;
            color: var(--text);
          }}

          .tarot-front .meta {{
            margin-top: 6px;
            color: rgba(255,255,255,0.78);
            font-size: 12px;
          }}

          .tarot-front .kw {{
            margin-top: 10px;
            color: var(--muted2);
            font-size: 11px;
          }}

          .tarot-front .meaning {{
            margin-top: 12px;
            color: var(--text);
            line-height: 1.65;
            font-size: 12px;
          }}

          .tarot-front .pad {{
            padding: 12px 12px 12px 12px;
          }}

          /* Slight hover lift */
          .tarot-card:hover .tarot-inner {{
            transform: translateY(-2px) rotateX(1deg);
          }}
          .tarot-card.is-revealed:hover .tarot-inner {{
            transform: translateY(-2px) rotateY(180deg) rotateX(1deg);
          }}

          /* Make overall typography a bit clearer */
          .stApp, .stApp p, .stApp li, .stApp label {{
            letter-spacing: 0.01em;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _tarot_card_html(d: DrawnCard, position: str, *, revealed: bool) -> str:
    kws = " · ".join(d.card.keywords) if d.card.keywords else ""
    rev_hint = "（逆位）" if d.is_reversed else "（正位）"
    cls = "tarot-card is-revealed" if revealed else "tarot-card"
    ill = _card_illustration_uri(d.card.id.zfill(2))
    return f"""
      <div class="{cls}">
        <div class="tarot-inner">
          <div class="tarot-face tarot-back"></div>
          <div class="tarot-face tarot-front">
            <div class="pad">
              <div class="ill" style="background-image: url('{ill}');"></div>
              <span class="badge">{position}</span>
              <div class="title">{d.card.name} {rev_hint}</div>
              <div class="kw">{kws}</div>
              <div class="meaning">{d.meaning}</div>
            </div>
          </div>
        </div>
      </div>
    """


def _cards_embed_html(inner_html: str) -> str:
    """
    Streamlit's markdown renderer can occasionally show long data-URI HTML as text.
    Rendering in an isolated HTML component is more reliable.
    """
    # Reuse the same card-back asset in the iframe.
    card_back = _asset_data_uri("assets/card_back.svg")
    return f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <style>
          :root {{
            --stroke: rgba(15, 23, 42, 0.10);
            --stroke2: rgba(15, 23, 42, 0.14);
            --text: rgba(15, 23, 42, 0.92);
            --muted: rgba(30, 41, 59, 0.72);
            --muted2: rgba(51, 65, 85, 0.60);
          }}
          body {{
            margin: 0;
            padding: 0;
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto;
          }}
          .tarot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            align-items: start;
            justify-items: center;
          }}
          /* Always keep 3-card spread in one row */
          .tarot-grid.three {{
            grid-template-columns: repeat(3, minmax(0, 220px));
            justify-content: center;
          }}
          .tarot-card {{
            position: relative;
            width: 100%;
            aspect-ratio: 7 / 11;
            border-radius: 16px;
            perspective: 1200px;
            max-width: 220px;
          }}
          .tarot-inner {{
            position: absolute;
            inset: 0;
            border-radius: 16px;
            transform-style: preserve-3d;
            transition: transform 720ms cubic-bezier(.2,.8,.2,1);
            box-shadow: 0 18px 42px rgba(15, 23, 42, 0.14), 0 1px 0 rgba(255,255,255,0.55) inset;
          }}
          .tarot-card.is-revealed .tarot-inner {{ transform: rotateY(180deg); }}
          .tarot-face {{
            position: absolute;
            inset: 0;
            border-radius: 16px;
            backface-visibility: hidden;
            overflow: hidden;
          }}
          .tarot-back {{
            background-image: url("{card_back}");
            background-size: cover;
            background-position: center;
            filter: saturate(1.05) contrast(1.0);
          }}
          .tarot-front {{
            transform: rotateY(180deg);
            background:
              radial-gradient(900px 500px at 30% 10%, rgba(168,85,247,0.10), rgba(0,0,0,0) 60%),
              radial-gradient(900px 500px at 80% 10%, rgba(56,189,248,0.08), rgba(0,0,0,0) 55%),
              linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.76));
            border: 1px solid var(--stroke2);
          }}
          .pad {{ padding: 12px; }}
          .ill {{
            width: 100%;
            height: 78px;
            border-radius: 12px;
            border: 1px solid var(--stroke);
            background-size: cover;
            background-position: center;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.12);
          }}
          .badge {{
            display: inline-block;
            margin-top: 10px;
            font-size: 11px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
            background: rgba(15, 23, 42, 0.04);
            border: 1px solid var(--stroke);
            padding: 5px 9px;
            border-radius: 999px;
          }}
          .title {{
            margin-top: 10px;
            font-size: 16px;
            font-weight: 760;
            color: var(--text);
          }}
          .kw {{
            margin-top: 8px;
            color: var(--muted2);
            font-size: 11px;
          }}
          .meaning {{
            margin-top: 10px;
            color: var(--text);
            line-height: 1.65;
            font-size: 12px;
          }}
        </style>
      </head>
      <body>
        {inner_html}
      </body>
    </html>
    """


st.set_page_config(page_title="Tarot GUI", page_icon="🔮", layout="wide")
_init_state()
_inject_theme()

st.markdown(
    """
    <div class="tg-header">
      <div style="font-size: 30px; font-weight: 850; letter-spacing: 0.02em; color: var(--text);">
        Tarot GUI
      </div>
      <div style="margin-top: 6px; color: var(--muted);">
        输入问题并抽牌。卡牌会先以牌背呈现；点击翻牌揭示解读。
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("设置")
    spread = st.selectbox(
        "牌阵",
        options=[SpreadType.SINGLE, SpreadType.THREE],
        format_func=lambda s: s.value,
    )
    allow_reversed = st.toggle("允许逆位", value=True)
    reversed_rate = st.slider("逆位概率", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
    use_seed = st.toggle("固定随机种子（便于复现）", value=False)
    seed = st.number_input("seed", min_value=0, max_value=1_000_000_000, value=20260409, step=1, disabled=not use_seed)
    animate_deal = st.toggle("抽牌动画（逐张发牌）", value=True)

st.divider()
question = st.text_input("你的问题", placeholder="例如：我该如何推进接下来的求职/感情/学习？")

cols = st.columns([1, 1, 2])
with cols[0]:
    draw_btn = st.button("抽牌", type="primary", use_container_width=True)
with cols[1]:
    clear_btn = st.button("清空历史", use_container_width=True)

if clear_btn:
    st.session_state.history = []
    st.toast("已清空历史。", icon="🧹")

cards = load_cards()

if draw_btn:
    if not question.strip():
        st.warning("请先输入一个问题（越具体越好）。")
    else:
        drawn = draw_spread(
            cards,
            spread,
            allow_reversed=allow_reversed,
            reversed_rate=float(reversed_rate),
            seed=int(seed) if use_seed else None,
        )

        # reset reveal state for the newest draw
        st.session_state.reveal = [False] * len(drawn)

        item: Dict[str, object] = {
            "ts": int(time.time()),
            "question": question.strip(),
            "spread": spread.value,
            "allow_reversed": bool(allow_reversed),
            "reversed_rate": float(reversed_rate),
            "seed": int(seed) if use_seed else None,
            "cards": [
                {
                    **asdict(d.card),
                    "is_reversed": d.is_reversed,
                    "orientation": d.orientation_label,
                    "meaning": d.meaning,
                }
                for d in drawn
            ],
        }
        st.session_state.history.insert(0, item)
        st.session_state.latest_ts = item["ts"]

st.subheader("本次解读")
if st.session_state.history:
    latest = st.session_state.history[0]
    st.write(f"**问题**：{latest['question']}")
    st.write(f"**牌阵**：{latest['spread']}")

    positions = spread_positions(SpreadType(latest["spread"]))
    drawn_cards: List[DrawnCard] = []
    for c in latest["cards"]:
        # 仅用于渲染，不做逻辑计算
        from tarot.logic import TarotCard

        card = TarotCard(
            id=str(c["id"]),
            name=str(c["name"]),
            keywords=tuple(c.get("keywords", [])),
            upright=str(c.get("upright", "")),
            reversed=str(c.get("reversed", "")),
        )
        drawn_cards.append(DrawnCard(card=card, is_reversed=bool(c["is_reversed"])))

    # reveal controls
    ctrl = st.columns([1, 1, 2])
    with ctrl[0]:
        if st.button("翻牌（全部）", use_container_width=True):
            st.session_state.reveal = [True] * len(drawn_cards)
    with ctrl[1]:
        if st.button("重新盖上", use_container_width=True):
            st.session_state.reveal = [False] * len(drawn_cards)

    # ensure reveal length matches cards length
    if not isinstance(st.session_state.reveal, list) or len(st.session_state.reveal) != len(drawn_cards):
        st.session_state.reveal = [False] * len(drawn_cards)

    # optional "deal" animation only for latest draw
    is_latest = st.session_state.latest_ts == latest.get("ts")
    grid_cls = "tarot-grid three" if len(drawn_cards) == 3 else "tarot-grid"
    if animate_deal and is_latest:
        placeholder = st.empty()
        for k in range(1, len(drawn_cards) + 1):
            html = f'<div class="{grid_cls}">' + "".join(
                _tarot_card_html(
                    drawn_cards[i],
                    positions[i],
                    revealed=bool(st.session_state.reveal[i]),
                )
                for i in range(k)
            ) + "</div>"
            # render as component to avoid raw HTML/data-URI being shown as text
            with placeholder.container():
                components.html(_cards_embed_html(html), height=520, scrolling=False)
            time.sleep(0.12)
    else:
        html = f'<div class="{grid_cls}">' + "".join(
            _tarot_card_html(
                drawn_cards[i],
                positions[i],
                revealed=bool(st.session_state.reveal[i]),
            )
            for i in range(len(drawn_cards))
        ) + "</div>"
        components.html(_cards_embed_html(html), height=520, scrolling=False)
else:
    st.info("还没有抽牌记录。先在上面输入问题并点击“抽牌”。")

st.divider()
st.subheader("历史记录")
if st.session_state.history:
    for idx, h in enumerate(st.session_state.history[:20], start=1):
        with st.expander(f"{idx}. {h['question']}  —  {h['spread']}"):
            for i, c in enumerate(h["cards"]):
                st.write(f"- **{spread_positions(SpreadType(h['spread']))[i]}**：{c['name']}（{c['orientation']}）")
else:
    st.caption("历史为空。")

