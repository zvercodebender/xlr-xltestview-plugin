#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys, string, time
import com.xhaus.jyson.JysonCodec as json

RESPONSE_STATUS_CODE = 200

if xltestServer is None:
    print "No server provided."
    sys.exit(1)

xltestUrl = xltestServer['url']

credentials = CredentialsFallback(xltestServer, username, password).getCredentials()

xltestAPIUrl = '%s/execute/%s?%s' % (xltestUrl,testSpecificationName,properties)

xltestResponse = XLRequest(xltestAPIUrl, 'GET', None, credentials['username'], credentials['password'], 'application/json').send()

taskId = None
if xltestResponse.status == RESPONSE_STATUS_CODE:
    data = json.loads(xltestResponse.read())
    taskId = data["taskId"]
    print "XLTest execution running on %s with taskId: %s." % (xltestUrl,taskId)
else:
    print "Failed to execute test on XL Test"
    xltestResponse.errorDump()
    sys.exit(1)

# Checking and waiting until test is finished
running = True
uri = "%s/test/%s" % (xltestUrl,taskId)
time.sleep(5)
while(running):
    xltestResponse = XLRequest(uri, 'GET', None, credentials['username'], credentials['password'], 'application/json').send()

    if xltestResponse.status == RESPONSE_STATUS_CODE:
        data = xltestResponse.read()
        if "event: close" in data:
            running = False
            print "XLTest execution finished on %s." % (uri)
            if "\"qualification\":false" in data:
                print "The test run is qualified as: FAILED."
                sys.exit(1)
            elif "\"qualification\":true" in data:
                print "The test run is qualified as: PASSED."
            else:
                print "Could not find qualification result"
                sys.exit(1)
        else:
            time.sleep(2)
    else:
        print "Failed to execute test on XL Test"
        xltestResponse.errorDump()
        sys.exit(1)