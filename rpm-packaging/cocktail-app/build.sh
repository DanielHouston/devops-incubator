#!/bin/sh

MYAPP_VERSION=1.0.4
TOMCAT_VERSION=7.0.37

if [ $# -gt 1 ]; then
  MYAPP_VERSION=$1
  shift
fi

if [ $# -gt 1 ]; then
  TOMCAT_VERSION=$1
  shift
fi

ARTIFACT_GROUP="org/jmxtrans/embedded/samples"
ARTIFACT_ID="cocktail-app"
ARTIFACT_VERSION=$MYAPP_VERSION
ARTIFACT_TYPE="war"
ARTIFACT_RELEASE_REPOSITORY="http://repo1.maven.org/maven2"
ARTIFACT_SNAPSHOT_REPOSITORY="http://repository-jmxtrans.forge.cloudbees.com/snapshot"

TOMCAT_URL=http://mir2.ovh.net/ftp.apache.org/dist/tomcat/tomcat-7/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz
CATALINA_JMX_REMOTE_URL=http://mir2.ovh.net/ftp.apache.org/dist/tomcat/tomcat-7/v${TOMCAT_VERSION}/bin/extras/catalina-jmx-remote.jar

fetch_maven() {

	local ART_GROUP=`echo $1 | sed "s#\.#/#g"`
	local ART_ID=$2
	local ART_VERSION=$3
	local ART_TYPE=$4
  	local ART_RELEASE_REPOSITORY=$5
  	local ART_SNAPSHOT_REPOSITORY=$6

	echo "fetch_maven called with $@"

	case "$ART_VERSION" in

	    *SNAPSHOT* )
		    # SNAPSHOT mode, need to fetch metadata.xml to get latest artifact id
			ART_URL=$ART_SNAPSHOT_REPOSITORY/$ART_GROUP/$ART_ID

			rm -f maven-metadata.xml
			echo "fetching maven-metadata.xml from $ART_URL/$ART_VERSION/maven-metadata.xml"
			curl -s -L $ART_URL/$ART_VERSION/maven-metadata.xml -o maven-metadata.xml

			#
			# Single or Multi SNAPSHOT ?
			#
			XPATH_QUERY="/metadata/versioning/snapshot/timestamp/text()"
			ART_TIME_STAMP=`xpath maven-metadata.xml $XPATH_QUERY 2>/dev/null`

			XPATH_QUERY="/metadata/versioning/lastUpdated/text()"
			ART_LATEST_UPDATED=`xpath maven-metadata.xml $XPATH_QUERY 2>/dev/null`

			XPATH_QUERY="/metadata/versioning/snapshot/buildNumber/text()"
			ART_BUILD_NUMBER=`xpath maven-metadata.xml $XPATH_QUERY 2>/dev/null`

			echo "ART_TIME_STAMP=$ART_TIME_STAMP ART_LATEST_UPDATED=$ART_LATEST_UPDATED ART_BUILD_NUMBER=$ART_BUILD_NUMBER"
			rm -f maven-metadata.xml

		    if [ -z "$ART_LATEST_UPDATED" ]; then
				echo "problem downloading metadata, aborting build"
		        exit -1
			fi

		    if [ -z "$ART_TIME_STAMP" ]; then
				echo "Single SNAPSHOT repository"
				# 1.0.0-SNAPSHOT-20120106100703
				ART_UNIQ_VERSION=$ART_VERSION-$ART_LATEST_UPDATED
				# basic-perf-webapp-1.0.0-SNAPSHOT.war
				ARTIFACT_REPO_FILE_NAME=$ART_ID-$ART_VERSION.$ART_TYPE
			else
		        echo "Multi SNAPSHOT repository"
		        # 1.0.0-20120106.100703-18
				ART_UNIQ_VERSION=$ART_VERSION-$ART_BUILD_NUMBER
				# basic-perf-webapp-1.0.0-20120106.100703-18.war
				ARTIFACT_REPO_FILE_NAME=`echo $ART_ID-$ART_VERSION-$ART_TIME_STAMP-$ART_BUILD_NUMBER.$ART_TYPE | sed "s#-SNAPSHOT##"`
			fi

			ARTIFACT_DOWNLOAD_URL=$ART_SNAPSHOT_REPOSITORY/$ART_GROUP/$ART_ID/$ART_VERSION
			ARTIFACT_RPM_FILE_NAME=$ART_ID-$ART_UNIQ_VERSION.$ART_TYPE
			ARTIFACT_RPM_VERSION=`echo $ART_VERSION | sed "s#-SNAPSHOT##"`
			ARTIFACT_RPM_RELEASE=0.$ART_LATEST_UPDATED
		;;

	    * )
			ARTIFACT_DOWNLOAD_URL=$ART_RELEASE_REPOSITORY/$ART_GROUP/$ART_ID/$ART_VERSION
			ARTIFACT_REPO_FILE_NAME=$ART_ID-$ART_VERSION.$ART_TYPE
			ARTIFACT_RPM_FILE_NAME=$ARTIFACT_REPO_FILE_NAME
			ARTIFACT_RPM_VERSION=$ART_VERSION
			ARTIFACT_RPM_SUBRELEASE=${ART_VERSION#*-}
			
			if [ -z "$ARTIFACT_RPM_SUBRELEASE" ]; then
				ARTIFACT_RPM_SUBRELEASE=0
			fi
			
			ARTIFACT_RPM_RELEASE=1.$ARTIFACT_RPM_SUBRELEASE
	   ;;

	esac
}

download_file_if_needed()
{
	URL=$1
	DEST=$2

	if [ ! -f $DEST ]; then

		echo "downloading from $URL to $DEST..."
		curl -L $URL -o $DEST

		case $DEST in
			*.tar.gz)
	        	tar tzf $DEST >>/dev/null 2>&1
	        	;;
	    	*.zip)
	        	unzip -t $DEST >>/dev/null 2>&1
	        	;;
	    	*.jar)
	        	unzip -t $DEST >>/dev/null 2>&1
	        	;;
	    	*.war)
	        	unzip -t $DEST >>/dev/null 2>&1
	        	;;
		esac

		if [ $? != 0 ]; then
			rm -f $DEST
			echo "invalid content for `basename $DEST` downloaded from $URL, discarding content and aborting build."
			exit -1
		fi

	fi
}

fetch_maven $ARTIFACT_GROUP $ARTIFACT_ID $ARTIFACT_VERSION $ARTIFACT_TYPE $ARTIFACT_RELEASE_REPOSITORY $ARTIFACT_SNAPSHOT_REPOSITORY
echo "Artifactoru Download URL is $ARTIFACT_DOWNLOAD_URL, Artifact repo name is $ARTIFACT_REPO_FILE_NAME, RPM source file is $ARTIFACT_RPM_FILE_NAME"

TOMCAT_URL=http://mir2.ovh.net/ftp.apache.org/dist/tomcat/tomcat-7/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz
CATALINA_JMX_REMOTE_URL=http://mir2.ovh.net/ftp.apache.org/dist/tomcat/tomcat-7/v${TOMCAT_VERSION}/bin/extras/catalina-jmx-remote.jar

download_file_if_needed ${TOMCAT_URL} SOURCES/apache-tomcat-${TOMCAT_VERSION}.tar.gz
download_file_if_needed ${CATALINA_JMX_REMOTE_URL} SOURCES/catalina-jmx-remote.jar

echo "Version to package Cocktail App $MYAPP_VERSION is powered by Apache Tomcat $TOMCAT_VERSION"

# prepare fresh directories
rm -rf BUILD RPMS SRPMS TEMP
mkdir -p BUILD RPMS SRPMS TEMP

# Build using rpmbuild (use double-quote for define to have shell resolv vars !)
rpmbuild -bb --define="_topdir $PWD" --define="_tmppath $PWD/TEMP" --define="TOMCAT_REL $TOMCAT_VERSION" \
             --define="APP_VERSION $ARTIFACT_RPM_VERSION" --define="APP_RELEASE $ARTIFACT_RPM_RELEASE" \
             --define "APP_WAR_FILE $ARTIFACT_RPM_FILE_NAME" SPECS/myapp.spec

