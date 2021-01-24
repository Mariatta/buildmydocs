import asyncio
import os
import sys
import traceback

import aiohttp
import cachetools
from aiohttp import web
from gidgethub import aiohttp as gh_aiohttp
from gidgethub import routing, sansio
from gidgethub.apps import get_installation_access_token

router = routing.Router()
cache = cachetools.LRUCache(maxsize=500)

routes = web.RouteTableDef()
from webservice.readthedocs_api import ReadthedocsAPI


@routes.get("/", name="home")
async def handle_get(request):
    return web.Response(text="This is buildmydocs app by Mariatta.")


@routes.post("/webhook")
async def webhook(request):
    try:
        body = await request.read()
        secret = os.environ.get("GH_SECRET")
        event = sansio.Event.from_http(request.headers, body, secret=secret)
        if event.event == "ping":
            return web.Response(status=200)
        async with aiohttp.ClientSession() as session:
            gh = gh_aiohttp.GitHubAPI(session, "demo", cache=cache)

            await asyncio.sleep(1)
            await router.dispatch(event, gh)
        try:
            print("GH requests remaining:", gh.rate_limit.remaining)
        except AttributeError:
            pass
        return web.Response(status=200)
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        return web.Response(status=500)


@router.register("installation", action="created")
@router.register("installation_repositories", action="added")
async def repo_installation_added(event, gh, *args, **kwargs):
    installation_id = event.data["installation"]["id"]
    installation_access_token = await get_installation_access_token(
        gh,
        installation_id=installation_id,
        private_key=os.environ.get("GH_PRIVATE_KEY"),
        app_id=os.environ.get("GH_APP_ID"),
    )
    if event.data['action'] == "added":
        repositories = event.data["repositories_added"]
    else:
        repositories = event.data["repositories"]
    for repository in repositories:
        url = f"/repos/{repository['full_name']}/issues"
        response = await gh.post(
            url,
            data={
                "title": "BuildMyDocs App installed!",
                "message": f'Thanks for installing, @{event.data["sender"]["login"]}. A ReadTheDocs project will be set up soon.',
            },
            oauth_token=installation_access_token["token"],
        )

        async with aiohttp.ClientSession() as session:
            rtd_api = ReadthedocsAPI(session, oauth_token=os.environ.get("RTD_AUTH"))
            resp = await rtd_api.post(
                "projects/",
                data={
                    "name": repository["name"],
                    "repository": {
                        "url": f"https://github.com/{repository['full_name']}",
                        "type": "git",
                    },
                    "homepage": f"https://github.com/{repository['full_name']}",
                    "programming_language": "py",
                    "language": "en",
                },
            )
            rtd_project_slug = resp["slug"]
            await rtd_api.patch(
                f"projects/{rtd_project_slug}/", data={"external_builds_enabled": True}
            )
            issue_url = response["url"]
            await gh.post(
                f"{issue_url}/comments",
                accept="application/vnd.github.v3+json",
                data=f"RTD project created at {resp['urls']['documentation']} on {resp['created']}",
                oauth_token=installation_access_token["token"],
            )
            await gh.patch(
                issue_url,
                data={"state": "closed"},
                oauth_token=installation_access_token["token"],
            )


if __name__ == "__main__":  # pragma: no cover
    app = web.Application()

    app.router.add_routes(routes)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)
    web.run_app(app, port=port)
