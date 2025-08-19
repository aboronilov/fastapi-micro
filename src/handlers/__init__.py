# This file makes the handlers directory a Python package
from .tasks import router as tasks_router
from .ping import router as ping_router

routers = [tasks_router, ping_router]