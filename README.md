# laika-py: A Python Client for Laika Feature-Flag Service

Import this module to use Laika feature-flag service in your application.

You should use this like a database connection in your app. It should live
within the application process, you should not initialize it per-request.

Basic usage is shown below:

```
from laika.client import Client as LaikaClient

lk = LaikaClient("http://baseurl", "username", "password", "env-name")
lk.init_timer(interval=10.0) # poll and update per 10 seconds

from flask import Flask

app = Flask(__name__)

@app.route("/<flag>")
def flag_state(flag):
    state = lk.get_state(flag)
    return f"{flag} is: {state}\n"

```

If you need consistent results you can use `lk.get_state(flag, on_demand=True)`
But be aware that it sends a HTTP request on each call synchronously. Which may
slow down your application and increase traffic load!

See [medigo/laika](https://github.com/medigo/laika.git) for more information.
The `client.py` implements most of the endpoints with related arguments described
in the original documentation.
