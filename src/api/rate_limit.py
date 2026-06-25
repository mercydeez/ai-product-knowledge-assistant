"""Shared slowapi Limiter instance for the Groq-backed /ask routes.

Lives in its own module (not api/app.py) so api/routes.py can import it
without a circular import — app.py already imports `router` from routes.py.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
