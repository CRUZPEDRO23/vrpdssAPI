try:
    from ._interfaces import interface, route
except ImportError:
    from _interfaces import interface, route

try:
    from .Heuristica import Heuristica
except ImportError:
    from Heuristica import Heuristica
