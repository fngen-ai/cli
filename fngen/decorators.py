from typing import Literal

from fngen.resources import Fleet


def webapp(framework: Literal['fastapi', 'flask', 'django'],
           fleet: Fleet | None = None):
    """
    Define a webapp
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
