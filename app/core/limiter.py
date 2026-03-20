from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed by IP address. In production, consider keying by clerk_user_id instead.
limiter = Limiter(key_func=get_remote_address)
