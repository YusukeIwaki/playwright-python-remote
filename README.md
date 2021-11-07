# playwright-remote

Enables us to execute [playwright-python](https://github.com/microsoft/playwright-python) scripts on **Pure-Python environment**.

![image](README/structure.png)

## Setup

```
pip install git+https://github.com/YusukeIwaki/playwright-python-remote
```

## Example

For communicating with Playwright server:

```py
from playwright_remote.sync_api import sync_playwright_remote

with sync_playwright_remote('ws://127.0.0.1:8080/ws') as playwright:
  with playwright.chromium.launch() as browser:
    page = browser.new_page()
    page.goto('https://github.com/YusukeIwaki')
    page.screenshot(path='YusukeIwaki.png')
```

Just replace `sync_playwright` with `sync_playwright_remote('ws://xxxxxxx/ws')`.

---

For communicating with Playwright Browser server:

```py
from playwright_remote.sync_api import connect_to_browser

with connect_to_browser('ws://127.0.0.1:xxxxx/xxxxxxxxxxxxxxxxxxxxxx') as browser:
  page = browser.new_page()
  page.goto('https://github.com/YusukeIwaki')
  page.screenshot(path='YusukeIwaki.png')
```


### Launch Playwright server

We have to prepare Playwright server using playwright CLI.

In local development environment (Node.js is required), just execute:

```
npx playwright@1.16.0 install && npx playwright@1.16.0 run-server
```

For deploying to PaaS servers, we can use Playwright official Docker image: https://hub.docker.com/_/microsoft-playwright

```Dockerfile
FROM mcr.microsoft.com/playwright:v1.16.0

WORKDIR /root
RUN npm install playwright@1.16.0 && ./node_modules/.bin/playwright install
CMD ["./node_modules/.bin/playwright", "run-server"]
```

Heroku example can be found [here](https://github.com/YusukeIwaki/playwright-python-playWithWebSocket/blob/main/heroku.yml).

### Launch Playwright Browser server

We can also share only one browser environment via WebSocket.

```
npx playwright@1.16.0 install && npx playwright@1.16.0 launch-server firefox
```

Note that the functionality of CLI for launch-server is not so rich.
For sharing more detailed environment, we have to prepare JavaScript server code like below:

```js
const playwright = require('playwright')

// https://playwright.dev/docs/api/class-browsertype/#browser-type-launch-server
option = {
  channel: 'chrome-canary',
  headless: false,
  port: 8080,
}
playwright.chromium.launchServer(option).then((server) => { console.log(server.wsEndpoint()) })
```

### Execute Python script on Alpine Linux environment

Since playwright-remote works on Pure-Python environment, it works also on Alpine Linux.

Unfortunately, `pip install playwright` cannot be executed on Alpine. We have to install playwright from git at this moment.

```Dockerfile
FROM python:3.9-alpine

RUN apk add --no-cache --virtual .install-deps build-base curl git \
    && pip install git+https://github.com/microsoft/playwright-python@v1.16.0 \
    && pip install git+https://github.com/YusukeIwaki/playwright-python-remote \
    && apk del .install-deps
```

Now, we can enjoy Playwright on the Docker image :)
Note that WebSocket endpoint URL should be set properly to `sync_playwright_remote("ws://xxxxxxxxx/ws")`.
