from .ping import router as ping_router
from .tasks import router as tasks_router
from .redis_health import router as redis_router

routers = [ping_router, tasks_router, redis_router]


