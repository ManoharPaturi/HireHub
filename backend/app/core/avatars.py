# Profile avatar helper. The user ID chooses a stable image from the selected
# pool, so fetching a profile repeatedly does not change its assigned portrait.

"""Deterministic gender-aware avatar selection (curated Unsplash portraits)."""

# Curated professional headshots from Unsplash (royalty-free).
# `pick_avatar` returns one deterministically by seed so each user keeps a
# stable avatar rather than a random one on every load.
_MALE_AVATARS = [
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1463453091185-61582044d556?auto=format&fit=crop&w=300&q=80",
]

_FEMALE_AVATARS = [
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80",
]

_NEUTRAL_AVATARS = [
    "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1607746882042-944635dfe10e?auto=format&fit=crop&w=300&q=80",
]


# Normalize the gender value, select its image pool, and use modulo
# to keep the ID-based index inside that pool.
def pick_avatar(gender: str | None, seed: int = 0) -> str:
    """Return a stable avatar URL for the given gender and seed (user id)."""
    g = (gender or "").strip().lower()
    if g == "male":
        pool = _MALE_AVATARS
    elif g == "female":
        pool = _FEMALE_AVATARS
    else:
        pool = _NEUTRAL_AVATARS
    return pool[seed % len(pool)] if pool else _NEUTRAL_AVATARS[0]
