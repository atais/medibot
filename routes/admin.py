import json
import os

from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse

from app_context import templates, get_current_user_context
from medicover.keywords import get_locations

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, user_context=Depends(get_current_user_context)):
    return templates.TemplateResponse(
        "admin.html",
        {
            "user": user_context.username,
            "request": request,
            "locations_data": None
        }
    )


@router.post("/admin", response_class=HTMLResponse)
async def admin_post(request: Request, user_context=Depends(get_current_user_context)):
    return templates.TemplateResponse(
        "admin.html",
        {
            "user": user_context.username,
            "request": request,
            "locations_data": None
        }
    )


@router.post("/admin/get-locations", response_class=HTMLResponse)
async def get_locations_endpoint(request: Request, user_context=Depends(get_current_user_context)):
    try:
        # Get locations data
        locations_response = get_locations(user_context.session)
        locations_dict = locations_response.model_dump()

        # Save to static/locations.json
        static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
        os.makedirs(static_dir, exist_ok=True)

        locations_file = os.path.join(static_dir, 'locations.json')
        with open(locations_file, 'w', encoding='utf-8') as f:
            json.dump(locations_dict, f, indent=2, ensure_ascii=False)

        # Format for display
        locations_json_str = json.dumps(locations_dict, indent=2, ensure_ascii=False)

        return templates.TemplateResponse(
            "admin.html",
            {
                "user": user_context.username,
                "request": request,
                "locations_data": locations_json_str,
                "success_message": "Locations saved to static/locations.json"
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "admin.html",
            {
                "user": user_context.username,
                "request": request,
                "locations_data": None,
                "error_message": f"Error fetching locations: {str(e)}"
            }
        )
