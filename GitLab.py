"""Waits for a request and calls a defined script.
Intended for recieving a POST message from GitLab and updating code.
"""
from twisted.internet import utils
from twisted.python import log
from twisted.web import resource

import pprint


class GitLab(resource.Resource):
    """Extends the twisted web interface to act like a web server
    """
    # End node, so reply
    isLeaf = True

    def __init__(self, script):
        """Execute script upon receiving POST request

        Arguments:
        script - path to script

        """
        self.script = script

    def render_POST(self, request):
        """Receive incoming POST request
        """
        # Log request
        log.msg('Received request: \n%s' % pprint.pformat(request.args))
        # Call update script
        output = utils.getProcessOutputAndValue(
            executable=self.script)
        # Look at result
        output.addCallbacks(self.write_response, self.no_response)
        return "Thanks!\n"

    def write_response(self, out):
        """Callback for if the script was called
        """
        stdout, stderr, exitcode = out
        # All good, log
        if exitcode == 0:
            log.msg('Updated repo.\nStdout:%s\nStderr:%s' % (stdout, stderr))
        # Something went wrong, log
        else:
            log.err('Update error!: %s\nStdout:%s\nStderr:%s' % (
                exitcode, stdout, stderr))

    def no_response(self, out):
        """Callback in case of script error: ie noexec, no such file
        Something went really bad.
        """
        stdout, stderr, exitcode = out
        log.err('Update error!: %s\nStdout: %s\nStderr:%s' % (
                exitcode, stdout, stderr))
