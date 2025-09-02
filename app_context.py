from fastapi.templating import Jinja2Templates

from user_context import UserContext

templates = Jinja2Templates(directory="templates")

user_contexts: dict[str, UserContext] = {}
