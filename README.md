wp-fingerprint
==============
Fingerprint a wordpress installation "passively" or actively for installed plugins. Attempts to version these plugins and includes a utility for generating more targeted lists of plugins. All 
modes have built in help dialogs (just use -h).

## Passive Scanning

"Passive" scanning works by documenting any plugins that may have its resources visible on the blog. These plugins are quick to identify, which is why passive scanning should always be done from 
the start. Once plugins have been identified, it attempts to version them by checking the readme.txt that comes with all wordpress plugins.

```
$ python finger.py --mode passive --host blog --path /
wp-fingerprint v0.0
Runing passive scan on blog

6 plugins found!
digg-digg [5.2.9]
wordpress-popular-posts [2.3.2]
google-analyticator [6.3.4]
ajax-quick-subscribe [2.0]
wp-minify [Couldn't Version, Unknown Error]
codecolorer [0.9.9]
```

## Active Scanning

Active scanning works by taking a list of known plugins, and checking if the directories exist in the blog. This type of scan can be really noisy, which is why it's better to use targeted lists or 
lists of known bad plugins. There is a list included. Once plugins have been identified, you can search for known exploits, or audit them yourselves (most of the time they're pretty shitty). This 
mode is threaded so it's super fast.

```
$ python finger.py --mode active --host blog --path / --list lists/known_bad.txt --threads 5
wp-fingerprint v0.0
Runing active scan on blog

2 plugins found!
content-slide [Unknown]
newsletter-subscription-optin-module [1.1.6]
```

## Generating Lists

If you don't want to use the lists included, you can make your own. This utility searches wordpress' plugin database and builds a list for you. You can search using a query or a tag. In this 
example, I searched for all plugins related to "timthumb" in the first 10 pages of the results. Because timthumb based plugins are known to have code execution bugs, you might want to use this 
list instead of the known_bad.txt.

```
$ python list_generator.py --search timthumb --pages 10 > /tmp/timthumb.txt
67 plugins documented.
```
