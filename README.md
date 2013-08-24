# Gitlab Hook Receiver

GitLab is pretty cool, and it even supports push hooks. But the way they're implemented, is that they send a POST request to a given url.

This simple receiver can launch a script (passed in as an argument during init) and/or contact [Pushover] on every recieved POST request, logs the request, as well as any output from the script. Its quite clean, and uses twisted's framework for calling the scripts.

There's no authentication, so use at your own risk, and preferably on an internal network. For some safety, no arguments are passed to the script. [Pushover] is a third party service, and if you enable it, some information will be passed to them in the pushover request.

## Requirements

* **pyOpenSSL** (for pushover support)

* **simplejson**

* **twisted**

## Pushover
To use [Pushover], edit **pushover.json**, which is an array of dictionaries with token/user. Messages will be sent to all token/user pairs. To have a nice icon: [logo-black.png]

![ScreenShot](ScreenShot.png)

## Usage
**GitLab.py** contains the code that listens in for a POST request, launches the script, contacts Pushover, and does logging. As you may have noticed, it does not contain a main...instead you launch it using **twistd**

**twistd** is a neat way of daemonizing _twisted_ servers, but suffers from a not so obvious way of how to pass in arguments. In this directory run:

```bash
twistd --help
```

You should see a _Gitlab_ command show up in the _Commands:_ list. This happens, because _twisted/plugins/GitLab\_plugin.py_ provides a service for _twistd_ to run. If you open that file, you'll see that it does some argument checking, and starts the service. To see options provided by the _GitLab_ receiver:

```bash
twistd GitLab --help
```

And finally to run, first pass in _twistd_ arguments, then _GitLab_ arguments. All GitLab arguments are optional.

```bash
twistd --pidfile=gitlab.pid -l gitlab.log GitLab --addr 127.0.0.1 --port 8504 --pushover pushover.json --script example.sh
```

[Pushover]:https://pushover.net/
[logo-black.png]:https://github.com/gitlabhq/gitlabhq/blob/master/app/assets/images/logo-black.png
