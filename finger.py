import argparse
import json
import Queue
import threading
import httplib
import urllib2
import time
import sys
import re

parser = argparse.ArgumentParser(description='Fingerprint a wordpress installation for known plugins. Both passive and active modes available.')
parser.add_argument("--host", help="specify the host")
parser.add_argument("--path", help="specify the path wordpress is installed")
parser.add_argument("--mode", help="specify whether to fingerprint passively or actively")
parser.add_argument("--list", help="if active fingerprinting, specify a list to use")
parser.add_argument("--useragent", help="useragent to send, default is firefox")
parser.add_argument("--ssl", help="whether to use ssl or not")
parser.add_argument("--threads", help="number of threads for active scanning", type=int)

args = parser.parse_args()

if not (args.host and args.path):
    print "You need to specify a host and a path!"
    sys.exit()

if not args.useragent:
    args.useragent = "Mozilla/5.0 (Windows NT 5.1; rv:8.0; en_us) Gecko/20100101 Firefox/8.0"

if not args.ssl:
    args.ssl = False

if not args.mode or args.mode != "active":
    args.mode = "passive"

if args.mode == "active" and not args.list:
    print "You need to supply a list of plugins to check for before using this mode."
    sys.exit()
elif args.mode == "active" and args.list:
    args.list = json.loads(open(args.list).read())

if not args.threads:
    args.threads = 5

print "wp-fingerprint v0.0"
print "Runing %s scan on %s" % (args.mode, args.host)
print ""

if args.mode and args.mode.lower() == "passive":
    if args.ssl:
        connection = httplib.HTTPSConnection(args.host)
    else:
        connection = httplib.HTTPConnection(args.host)

    try:
        connection.request('GET', args.path, '', {'User-Agent':args.useragent})
        data = connection.getresponse().read()
    except:
        print "Was not able to retrieve index. Try again?"
        sys.exit()

    plugins_regex = re.compile('wp-content/plugins/([\w\s\d\(\)\-]+)')
    plugins = list(set(plugins_regex.findall(data)))
    if plugins:
        print "%d plugins found!" % (len(plugins))
        for plugin in plugins:
            try:
                connection.request('GET', '%s/wp-content/plugins/%s/readme.txt' % (args.path, plugin), "", {'User-Agent':args.useragent})
                readme = connection.getresponse().read()
                print "%s [%s]" % (plugin, readme.split('Stable tag: ')[1].split('\n')[0].replace('\r',''))
            except:
                print "%s [Couldn't Version, Unknown Error]" % (plugin)
    else:
        print "Did not find any plugins :'{"
    sys.exit()

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def get_plugin_info(args, queue, plugin_info):
    plugin = plugin_info['path']

    if args.ssl:
        connection = httplib.HTTPSConnection(args.host)
    else:
        connection = httplib.HTTPConnection(args.host)

    connection.request("HEAD", "%s/wp-content/plugins/%s/" % (args.path, plugin), "", {'User-Agent':args.useragent})
    response = connection.getresponse()
        
    if response.status not in [404,301]:
        if args.ssl:
            connection = httplib.HTTPSConnection(args.host)
        else:
            connection = httplib.HTTPConnection(args.host)

        try:
            connection.request("GET", "%s/wp-content/plugins/%s/readme.txt" % (args.path, plugin), "", {'User-Agent':args.useragent})
            version = connection.getresponse().read().split('Stable tag: ')[1].split('\n')[0].replace('\r','')
        except:
            version = 'Unknown'
    else:
        version = 'n/a'

    queue.put({'plugin':plugin, 'status':response.status, 'version':version})

# plugins = '''e-commerce-mailcheck woocommerce newsletter-subscription-optin-module akismet hello-dolly'''.split()
plugins = chunks(args.list, args.threads)

queue = Queue.Queue()
responses = []
lastupdated = []
found = []

for chunk in plugins:
    for plugin in chunk:
        t = threading.Thread(target=get_plugin_info, args = (args, queue, plugin))
        t.daemon = True
        t.start()

    # All the threads were started, wait for responses
    for i in range(len(chunk)):
        response = queue.get()
        if response['status'] not in [404,301] and response['version'] <> 'n/a' and response['plugin'] not in found:
            responses.append({'plugin':response['plugin'], 'version':response['version']})
            found.append(response['plugin'])

    if responses != lastupdated:
        lastupdated = responses
        print "Current progress:"
        for response in responses:
            print '%s [%s]' % (response['plugin'], response['version'])

if responses:
    print "\nDone scanning! Results:"
    for response in responses:
        print '%s [%s]' % (response['plugin'], response['version'])
else:
    print "\nNo plugins were found. :'{"

