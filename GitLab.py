"""Waits for a request and calls a defined script / pushover
Intended for recieving a POST message from GitLab and updating code.
"""
from twisted.internet import utils
from twisted.python import log
from twisted.web import resource
from twisted.web.client import getPage

import pprint
import simplejson
import urllib


class GitLab(resource.Resource):
    """Extends the twisted web interface to act like a web server
    """
    # End node, so reply
    isLeaf = True

    def __init__(self, script=None, pushover=None):
        """Execute script upon receiving POST request

        Keyword Arguments:
        script - path to script
        pushover - array of pushover data

        """
        self.script = script
        self.pushover = pushover

    def render_POST(self, request):
        """Receive incoming POST request
        """
        # Read post data
        post_data = request.content.read()
        # Log request
        try:
            data = simplejson.loads(post_data)
            log.msg('Received request: \n%s' % pprint.pformat(data))
        except simplejson.JSONDecodeError:
            data = None
            log.err("JSON Parsing error for: %s" % post_data)
            raise
        if data is not None and self.pushover is not None and len(self.pushover) > 0:
            try:
                data = simplejson.loads(post_data)
                # 0 length commits arise from testing web hook in GitLab
                # To test, instead call the test script in the repo
                if len(data["commits"]) > 0:
                    # Name of user who pushed the commits
                    user = data["user_name"]
                    # Repository they were pushed to
                    repo = data["repository"]["name"]
                    # Number of commits pushed
                    commits = data["total_commits_count"]
                    # Message of last commit
                    message = data["commits"][-1]["message"]
                    # Url to last commit
                    commit_url = data["commits"][-1]["url"]

                    # Data to send to pushover
                    title = "%s pushed %s commit%s to %s" \
                            "" % (user, commits, 's' if commits > 1 else '',
                                  repo)
                    message = 'Latest: %s' % message
                    url = commit_url
                    url_title = "View commit on GitLab"
                    for p in self.pushover:
                        pushover_data = {
                            "token": p["token"],
                            "user": p["user"],
                            "title": title,
                            "message": message,
                            "url": url,
                            "url_title": url_title
                        }

                        # Now call pushover
                        # On failure, call pushover_fail and log the failure
                        getPage("https://api.pushover.net/1/messages.json",
                                method="POST",
                                postdata=urllib.urlencode(pushover_data),
                                headers={"Content-type": "application/x-www"
                                                         "-form-urlencoded"}
                                ).addCallbacks(self.pushover_response,
                                               self.pushover_fail)
            except simplejson.JSONDecodeError:
                log.err("JSON Parsing error for: %s" % post_data)
                return "Bad!"
            except KeyError as key:
                log.err("Missing key from JSON data: %s" % key)
                return "Bad!"

        # Call update script if one is configured
        if self.script is not None:
            output = utils.getProcessOutputAndValue(executable=self.script)
            # Look at result
            output.addCallbacks(self.script_response, self.no_script_response)
        return "Thanks!\n"

    def pushover_response(self, response):
        """Callback for a good pushover response
        """
        log.msg("Pushover ok - status: %s, request: %s"
                "" % (response["status"], response["request"]))

    def pushover_fail(self, response):
        """Callback for a failed pushover response
        """
        log.err("Pushover bad: %s" % response)

    def script_response(self, out):
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

    def no_script_response(self, out):
        """Callback in case of script error: ie noexec, no such file
        Something went really bad.
        """
        stdout, stderr, exitcode = out
        log.err('Update error!: %s\nStdout: %s\nStderr:%s' % (
                exitcode, stdout, stderr))
