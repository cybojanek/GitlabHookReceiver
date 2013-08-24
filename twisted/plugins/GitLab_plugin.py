from zope.interface import implements

from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.web import server

import simplejson
import sys

from GitLab import GitLab


class Options(usage.Options):
    optParameters = [
        ["port", "p", 8504, "The port number to listen on."],
        ["addr", "a", "127.0.0.1", "Address to listen on"],
        # Use "" to make them optional: None makes them required
        ["script", "s", "", "Script to call after each POST"],
        ["pushover", "o", "", "JSON array of Pushover credentials"]
    ]


class GitLabServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "GitLab"
    description = "Run this to listen to git repo updates"
    options = Options

    def makeService(self, options):
        """Construct a TCPServer from a factory defined in GitLab.
        """
        # Change from "" non used to something a bit more standard: None
        for k in ["script", "pushover"]:
            if options[k] == "":
                options[k] = None

        pushover = None
        if options["pushover"] is not None:
            try:
                with open(options["pushover"], "r") as p:
                    pushover = simplejson.loads(p.read())
            except IOError:
                sys.stderr.write("Could not open: %s\n" % options["pushover"])
            except simplejson.JSONDecodeError:
                sys.stderr.write("Could not parse JSON: %s\n"
                                 "" % options["pushover"])
            # Simple validation
            for p in pushover:
                for k in ["token", "user"]:
                    if k not in p:
                        sys.stderr.write("Missing: %s from pushover\n" % k)
                    if not isinstance(p[k], str):
                        sys.stderr.write("%s is not a string in %s\n"
                                         "" % (p[k], k))
        # Check that we're doing something
        if options["script"] is None and (pushover is None or
                                          len(pushover) == 0):
            sys.stderr.write("WARNING: script and pushover are both "
                             "empty. This will act as only a logger\n")
        gitlab = GitLab(options["script"], pushover)
        return internet.TCPServer(int(options["port"]),
                                  server.Site(gitlab),
                                  interface=options["addr"])


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = GitLabServiceMaker()
