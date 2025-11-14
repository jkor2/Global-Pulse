# Automatically load all category feed files and combine them

from .world import WORLD_FEEDS
from .politics import POLITICS_FEEDS
from .business import BUSINESS_FEEDS
from .tech import TECH_FEEDS
from .science import SCIENCE_FEEDS
from .sports import SPORTS_FEEDS
from .health import HEALTH_FEEDS
from .entertainment import ENTERTAINMENT_FEEDS
from .gaming import GAMING_FEEDS

from .canada import CANADA_FEEDS
from .india import INDIA_FEEDS
from .uk import UK_FEEDS
from .australia import AUSTRALIA_FEEDS

from .general_extra import EXTRA_FEEDS


RSS_FEEDS = {
    "world": WORLD_FEEDS,
    "politics": POLITICS_FEEDS,
    "business": BUSINESS_FEEDS,
    "technology": TECH_FEEDS,
    "science": SCIENCE_FEEDS,
    "sports": SPORTS_FEEDS,
    "health": HEALTH_FEEDS,
    "entertainment": ENTERTAINMENT_FEEDS,
    "gaming": GAMING_FEEDS,

    "canada": CANADA_FEEDS,
    "india": INDIA_FEEDS,
    "uk": UK_FEEDS,
    "australia": AUSTRALIA_FEEDS,

    "other": EXTRA_FEEDS,
}