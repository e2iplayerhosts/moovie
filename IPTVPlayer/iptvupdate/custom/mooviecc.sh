#!/bin/sh
echo "mooviecc.sh: start"
cp $1/iptvupdate/custom/mooviecc.sh $2/iptvupdate/custom/mooviecc.sh
status=$?
if [ $status -ne 0 ]; then
	echo "mooviecc.sh: Critical error. The $0 file can not be copied, error[$status]."
	exit 1
fi
cp $1/hosts/hostmooviecc.py $2/hosts/
hosterr=$?
cp $1/icons/logos/mooviecclogo.png $2/icons/logos/
logoerr=$?
cp $1/icons/PlayerSelector/mooviecc*.png $2/icons/PlayerSelector/
iconerr=$?
if [ $hosterr -ne 0 ] || [ $logoerr -ne 0 ] || [ $iconerr -ne 0 ]; then
	echo "mooviecc.sh: copy error from source hosterr[$hosterr], logoerr[$logoerr, iconerr[$iconerr]"
fi
wget --no-check-certificate https://github.com/e2iplayerhosts/mooviecc/archive/master.zip -q -O /tmp/mooviecc.zip
if [ -s /tmp/mooviecc.zip ] ; then
	unzip -q -o /tmp/mooviecc.zip -d /tmp
	cp -r -f /tmp/mooviecc-master/IPTVPlayer/hosts/hostmooviecc.py $2/hosts/
	hosterr=$?
	cp -r -f /tmp/mooviecc-master/IPTVPlayer/icons/* $2/icons/
	iconerr=$?
	if [ $hosterr -ne 0 ] || [ $iconerr -ne 0 ]; then
		echo "mooviecc.sh: copy error from mooviecc-master hosterr[$hosterr], iconerr[$iconerr]"
	fi
else
	echo "mooviecc.sh: mooviecc.zip could not be downloaded."
fi
rm -r -f /tmp/mooviecc*
echo "mooviecc.sh: exit 0"
exit 0