from zope.interface import implements

from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.web import server

from GitLab import GitLab

import sys


class Options(usage.Options):
    optParameters = [
        ["port", "p", 8504, "The port number to listen on."],
        ["addr", "a", "127.0.0.1", "Address to listen on"],
        ["script", "s", None, "Script to call after each POST"]
    ]


class GitLabServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "GitLab"
    description = "Run this to listen to git repo updates"
    options = Options

    def makeService(self, options):
        """Construct a TCPServer from a factory defined in GitLab.
        """
        if options["script"] is None:
            print "BAD SCRIPT: %r" % options["script"]
            sys.exit(1)
        return internet.TCPServer(int(options["port"]),
                                  server.Site(GitLab(options["script"])),
                                  interface=options["addr"])


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.

serviceMaker = GitLabServiceMaker()
