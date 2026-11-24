"""One FastMCP server per Council member. Each can run on its own: `python -m council.servers.trip`."""
from .trip import mcp as trip
from .outings import mcp as outings
from .wallet import mcp as wallet
from .time import mcp as time
from .health import mcp as health
from .family import mcp as family

GATEKEEPERS = {"trip": trip, "outings": outings, "wallet": wallet, "time": time}
ADVISORS = {"health": health, "family": family}
