import argparse
import json
import urllib
import urllib2
import re
import sys

parser = argparse.ArgumentParser(description='Generate the list of plugins to check for via active fingerprinting.')
parser.add_argument("--search", help="find plugins with a search keyword")
parser.add_argument("--tag", help="find plugins with a specific tag")
parser.add_argument("--pages", help="number of pages to go through in the search", type=int)

args = parser.parse_args()
regex = re.compile('<a href="http://wordpress.org/plugins/([a-z\-]+)/">([\w\s\d\(\)\-]+)</a>?')

if args.search:
    url = "http://wordpress.org/extend/plugins/search.php?q=%s&page=%d";
    search_term = args.search
elif args.tag:
    url = "http://wordpress.org/extend/plugins/tags/%s/page/%d"
    search_term = args.tag
else:
    print "You need to supply either a search term or a tag."
    sys.exit()

if args.pages <= 0:
    print "You need a positive number of pages."
    sys.exit()


plugins = []
names = []

for i in range(1, args.pages+1):
    content = urllib2.urlopen(url % (search_term, i)).read()
    results = regex.findall(content)
    for result in results:
        if result[1] not in names:
            names.append(result[1])
            plugins.append({'path':result[0], 'name':result[1]})
    if len(results) == 0:
        break

print json.dumps(plugins)
print >> sys.stderr, "%d plugins documented." % (len(plugins))
