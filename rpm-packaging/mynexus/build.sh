#!/bin/sh

NEXUS_VERSION=2.0.1
TOMCAT_VERSION=7.0.26

if [ $# -gt 1 ]; then
  NEXUS_VERSION=$1
  shift
fi

if [ $# -gt 1 ]; then
  TOMCAT_VERSION=$1
  shift
fi

NEXUS_URL=http://nexus.sonatype.org/downloads/nexus-webapp-${NEXUS_VERSION}.war
TOMCAT_URL=http://mir2.ovh.net/ftp.apache.org/dist/tomcat/tomcat-7/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz
CATALINA_JMX_REMOTE_URL=http://mir2.ovh.net/ftp.apache.org/dist/tomcat/tomcat-7/v${TOMCAT_VERSION}/bin/extras/catalina-jmx-remote.jar

if [ ! -f SOURCES/nexus-webapp-${NEXUS_VERSION}.war ]; then
  echo "downloading nexus-webapp-${NEXUS_VERSION}.war from $NEXUS_URL"
  curl -s -L $NEXUS_URL -o SOURCES/nexus-webapp-${NEXUS_VERSION}.war
fi

if [ ! -f SOURCES/apache-tomcat-${TOMCAT_VERSION}.tar.gz ]; then
  echo "downloading apache-tomcat-${TOMCAT_VERSION}.tar.gz from $TOMCAT_URL"
  curl -s -L $TOMCAT_URL -o SOURCES/apache-tomcat-${TOMCAT_VERSION}.tar.gz
fi

if [ ! -f SOURCES/catalina-jmx-remote-${TOMCAT_VERSION}.jar ]; then
  echo "downloading catalina-jmx-remote-${TOMCAT_VERSION}.jar from $CATALINA_JMX_REMOTE_URL"
  curl -s -L $CATALINA_JMX_REMOTE_URL -o SOURCES/catalina-jmx-remote-${TOMCAT_VERSION}.jar
fi

echo "Version to package is $NEXUS_VERSION, powered by Apache Tomcat $TOMCAT_VERSION"

# prepare fresh directories
rm -rf BUILD RPMS SRPMS TEMP
mkdir -p BUILD RPMS SRPMS TEMP

# Build using rpmbuild (use double-quote for define to have shell resolv vars !)
rpmbuild -ba --define="_topdir $PWD" --define="_tmppath $PWD/TEMP" --define="TOMCAT_REL $TOMCAT_VERSION" --define="NEXUS_REL $NEXUS_VERSION"  SPECS/mynexus.spec

