from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

# Global dictionary to store user contexts
user_contexts = {}
