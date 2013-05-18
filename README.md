# gitlab hook receiver

GitLab is pretty cool, and it even supports push hooks. But the way they're implemented, is that they send a POST request to a given url.

This simple receiver launches a script (passed in as an argument during init), on every recieved POST request, and logs the request, as well as any output from the script. Its quite clean, and uses twisted's framework for calling the scripts.

There's no authentication, so use at your own risk, and preferably internally.

## Usage
**GitLab.py** contains the code that listens in for a POST request, launches the script, and does logging. As you may have noticed, it does not contain a main...instead you launch it using **twistd**

**twistd** is a neat way of daemonizing _twisted_ servers, but suffers from a not so obvious way of how to pass in arguments. In this directory run:

```bash
twistd --help
```

You should see a _Gitlab_ command show up in the _Commands:_ list. This happens, because _twisted/plugins/GitLab\_plugin.py_ provides a service for _twistd_ to run. If you open that file, you'll see that it does some argument checking, and starts the service. To see options provided by the _GitLab_ receiver:

```bash
twistd GitLab --help
```

And finally to run, first pass in _twistd_ arguments, then _GitLab_ arguments.

```bash
twistd --pidfile=gitlab.pid -l gitlab.log GitLab --addr 10.0.0.5 --script example.sh
```