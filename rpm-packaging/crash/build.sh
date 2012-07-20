#!/bin/sh

#VERSION=1.0.0
VERSION=1.1.0-cr1

# prepare fresh directories
rm -rf BUILD RPMS SRPMS TEMP
mkdir -p BUILD RPMS SRPMS SOURCES TEMP

CRASH_URL=http://crsh.googlecode.com/files/crsh-${VERSION}.tar.gz

if [ ! -f SOURCES/crsh-${VERSION}.tar.gz ]; then
  echo "downloading crsh-${VERSION}.tar.gz from $CRASH_URL"
curl -s -L $CRASH_URL -o SOURCES/crsh-${VERSION}.tar.gz
fi

# Build using rpmbuild (use double-quote for define to have shell resolv vars !)
rpmbuild -bb --define="_topdir $PWD" --define="_tmppath $PWD/TEMP" --define="VERSION $VERSION" SPECS/crash.spec

