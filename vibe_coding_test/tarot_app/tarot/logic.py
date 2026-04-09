from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


class SpreadType(str, Enum):
    SINGLE = "单张牌"
    THREE = "三张牌（过去/现在/未来）"


@dataclass(frozen=True)
class TarotCard:
    id: str
    name: str
    keywords: Tuple[str, ...]
    upright: str
    reversed: str


@dataclass(frozen=True)
class DrawnCard:
    card: TarotCard
    is_reversed: bool

    @property
    def orientation_label(self) -> str:
        return "逆位" if self.is_reversed else "正位"

    @property
    def meaning(self) -> str:
        return self.card.reversed if self.is_reversed else self.card.upright


def _data_path() -> str:
    return os.path.join(os.path.dirname(__file__), "cards_zh.json")


def load_cards(path: Optional[str] = None) -> List[TarotCard]:
    p = path or _data_path()
    with open(p, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = json.load(f)
    cards: List[TarotCard] = []
    for c in data.get("cards", []):
        cards.append(
            TarotCard(
                id=str(c["id"]),
                name=str(c["name"]),
                keywords=tuple(c.get("keywords", [])),
                upright=str(c.get("upright", "")),
                reversed=str(c.get("reversed", "")),
            )
        )
    if not cards:
        raise ValueError("No tarot cards loaded.")
    return cards


def draw_spread(
    cards: Sequence[TarotCard],
    spread: SpreadType,
    *,
    allow_reversed: bool = True,
    reversed_rate: float = 0.5,
    seed: Optional[int] = None,
) -> List[DrawnCard]:
    rng = random.Random(seed)
    n = 1 if spread == SpreadType.SINGLE else 3
    picked = rng.sample(list(cards), k=n)

    out: List[DrawnCard] = []
    for card in picked:
        is_rev = allow_reversed and (rng.random() < reversed_rate)
        out.append(DrawnCard(card=card, is_reversed=is_rev))
    return out


def spread_positions(spread: SpreadType) -> List[str]:
    if spread == SpreadType.SINGLE:
        return ["指引"]
    return ["过去", "现在", "未来"]

