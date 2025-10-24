from typing import Literal
from fngen.resources import Fleet


def webapp(hostname: str,
           framework: Literal['fastapi', 'flask', 'django'],
           fleet: Fleet | None = None):
    """
    Mark a function for deployment as a webapp on FNGEN
    """
    def g(f):
        # intentionally do nothing :)
        return f
    return g


# def task_worker(compute='server'):
#     """
#     Coming soon
#     """
#     def g(f):
#         # intentionally do nothing :)
#         return f
#     return g
