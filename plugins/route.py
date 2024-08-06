from aiohttp import web
from utils import temp

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    raise web.HTTPFound(f"https://telegram.me/{temp.U_NAME}")

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app