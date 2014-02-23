import web
import jinja2
import os
import json
from thingdb import Thing

urls = (
    "/(.*).json", "thing_json",
    "/(.*)", "thing"
)
app = web.application(urls, globals())

def get_jinja2_env():
    root = os.path.join(os.path.dirname(__file__), "templates")
    return jinja2.Environment(loader=jinja2.FileSystemLoader(root))

jinja_env = get_jinja2_env()
def render_template(filename, **kwargs):
    template = jinja_env.get_template(filename)
    return template.render(**kwargs)

class thing:
    def GET(self, key):
        t = Thing.find(key)
        if not t:
            raise web.notfound()
        template = t.type.lower() + ".html"
        return render_template(template, thing=t)

def json_notfound():
    return web.HTTPError("404 Not Found", {"Content-Type": "application/json"}, '{"error": "not found"}')

class thing_json:
    def GET(self, key):
        t = Thing.find(key)
        if not t:
            raise json_notfound()
        web.header("Content-Type", "application/json")
        return json.dumps(t.info)

if __name__ == "__main__":
    app.run()
