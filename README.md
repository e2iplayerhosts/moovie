E2iPlayer mooviecc HU host

Install:

~~~
wget --no-check-certificate https://github.com/e2iplayerhosts/mooviecc/archive/master.zip -q -O /tmp/mooviecc.zip
unzip -q -o /tmp/mooviecc.zip -d /tmp
cp -r -f /tmp/mooviecc-master/IPTVPlayer/* /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer
rm -r -f /tmp/mooviecc*
~~~

restart enigma2 GUI
