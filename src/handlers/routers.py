from .ping import router as ping_router
from .tasks import router as tasks_router
from .redis_health import router as redis_router
from .auth import router as auth_router
from .users import router as users_router
from .oauth import router as oauth_router

routers = [ping_router, tasks_router, redis_router, auth_router, users_router, oauth_router]


