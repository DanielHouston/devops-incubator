%if %{?TOMCAT_REL:1}
%define tomcat_rel        %{TOMCAT_REL}
%else
%define tomcat_rel        7.0.23
%endif

%if %{?SONAR_REL:1}
%define sonar_rel    %{SONAR_REL}
%else
%define sonar_rel    2.12
%endif

Name: mysonar
Version: 1.0.0
Release: 1
Summary: Sonar %{sonar_rel} powered by Apache Tomcat %{tomcat_rel}
Group: Applications/Communications
URL: http://www.mycorp.org/
Vendor: MyCorp
Packager: MyCorp
License: AGPLv1
BuildArch:  noarch

%define myapp             mysonar
%define myappusername     mysonar
%define myappuserid       1237
%define myappgroupid      1237

%define myappdir          /opt/%{myapp}
%define myappdatadir      %{_var}/lib/%{myapp}
%define myapplogdir       %{_var}/log/%{myapp}
%define myappexec         %{myappdir}/bin/catalina.sh
%define myappconfdir      %{myappdir}/conf
%define myappwebappdir    %{myappdir}/webapps
%define myapptempdir      /tmp/%{myapp}
%define myappworkdir      %{_var}/%{myapp}

%define _systemdir        /lib/systemd/system
%define _initrddir        %{_sysconfdir}/init.d

BuildRoot: %{_tmppath}/build-%{name}-%{version}-%{release}

%if 0%{?suse_version} > 1140
BuildRequires: systemd
%{?systemd_requires}
%endif

BuildRequires:      unzip

Requires:           java = 1.6.0
Requires(pre):      %{_sbindir}/groupadd
Requires(pre):      %{_sbindir}/useradd

Requires(preun):    %{_sbindir}/groupdel
Requires(preun):    %{_sbindir}/userdel

Source0: apache-tomcat-%{tomcat_rel}.tar.gz
Source1: sonar-%{sonar_rel}.zip
Source2: myapp-initd
Source3: myapp-sysconfig
Source4: myapp-jmxremote.access.skel
Source5: myapp-jmxremote.password.skel
Source6: myapp-setenv.sh
Source7: myapp-logrotate
Source8: myapp-server.xml.skel
Source9: myapp-limits.conf
Source10: myapp-systemd
Source11: catalina-jmx-remote-%{tomcat_rel}.jar
Source12: sonar.properties

%description
Jenkins %{jenkins_rel} powered by Apache Tomcat

%prep
%setup -q -c

%build
unzip %{SOURCE1}
cp -f %{SOURCE12} sonar-%{sonar_rel}/conf
pushd sonar-%{sonar_rel}/war >>/dev/null
./build-war.sh
popd >>/dev/null

%install
# Prep the install location.
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/security/limits.d
mkdir -p $RPM_BUILD_ROOT%{_systemdir}

mkdir -p $RPM_BUILD_ROOT%{myappdir}
mkdir -p $RPM_BUILD_ROOT%{myappdatadir}
mkdir -p $RPM_BUILD_ROOT%{myappdatadir}/conf
mkdir -p $RPM_BUILD_ROOT%{myapplogdir}
mkdir -p $RPM_BUILD_ROOT%{myapptempdir}
mkdir -p $RPM_BUILD_ROOT%{myappworkdir}
mkdir -p $RPM_BUILD_ROOT%{myappwebappdir}

# Copy tomcat
mv apache-tomcat-%{tomcat_rel}/* $RPM_BUILD_ROOT%{myappdir}

# remove default webapps
rm -rf $RPM_BUILD_ROOT%{myappdir}/webapps/*

# patches to have logs under /var/log/myapp
sed -i 's|\${catalina.base}/logs|%{myapplogdir}|g' $RPM_BUILD_ROOT%{myappdir}/conf/logging.properties

# copy Sonar generated webapp as ROOT.war (will respond to /)
cp sonar-%{sonar_rel}/war/sonar.war  $RPM_BUILD_ROOT%{myappwebappdir}/ROOT.war

# copy logback.xml in SONAR_HOME/conf
cp sonar-%{sonar_rel}/conf/logback.xml $RPM_BUILD_ROOT%{myappdatadir}/conf
# copy sonar.properties also in SONAR_HOME/conf
cp %{SOURCE12} $RPM_BUILD_ROOT%{myappdatadir}/conf
# copy required stuff in SONAR_HOME
cp -r sonar-%{sonar_rel}/extras $RPM_BUILD_ROOT%{myappdatadir}
cp -r sonar-%{sonar_rel}/extensions $RPM_BUILD_ROOT%{myappdatadir}
find $RPM_BUILD_ROOT%{myappdatadir}/extensions -type f -name "*.jar" -exec chmod 644 \{\} \;
cp -r sonar-%{sonar_rel}/lib $RPM_BUILD_ROOT%{myappdatadir}
# data dir (if derby usage)
mkdir -p $RPM_BUILD_ROOT%{myappdatadir}/data

# init.d
cp  %{SOURCE2} $RPM_BUILD_ROOT%{_initrddir}/%{myapp}
sed -i 's|@@SKEL_APP@@|%{myapp}|g' $RPM_BUILD_ROOT%{_initrddir}/%{myapp}
sed -i 's|@@SKEL_USER@@|%{myappusername}|g' $RPM_BUILD_ROOT%{_initrddir}/%{myapp}
sed -i 's|@@SKEL_VERSION@@|version %{VERSION} release %{RELEASE}|g' $RPM_BUILD_ROOT%{_initrddir}/%{myapp}
sed -i 's|@@SKEL_EXEC@@|%{myappexec}|g' $RPM_BUILD_ROOT%{_initrddir}/%{myapp}

# sysconfig
cp  %{SOURCE3}  $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{myapp}
sed -i 's|@@SKEL_APP@@|%{myapp}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{myapp}
sed -i 's|@@SKEL_APPDIR@@|%{myappdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{myapp}
sed -i 's|@@SKEL_DATADIR@@|%{myappdatadir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{myapp}
sed -i 's|@@SKEL_LOGDIR@@|%{myapplogdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{myapp}
sed -i 's|@@SKEL_USER@@|%{myappusername}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{myapp}
sed -i 's|@@SKEL_CONFDIR@@|%{myappconfdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{myapp}

# JMX (including JMX Remote)
cp %{SOURCE11} $RPM_BUILD_ROOT%{myappdir}/lib
cp %{SOURCE4}  $RPM_BUILD_ROOT%{myappconfdir}/jmxremote.access.skel
cp %{SOURCE5}  $RPM_BUILD_ROOT%{myappconfdir}/jmxremote.password.skel

# Our custom setenv.sh to get back env variables
cp  %{SOURCE6} $RPM_BUILD_ROOT%{myappdir}/bin/setenv.sh
sed -i 's|@@SKEL_APP@@|%{myapp}|g' $RPM_BUILD_ROOT%{myappdir}/bin/setenv.sh

# Install logrotate
cp %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{myapp}
sed -i 's|@@SKEL_LOGDIR@@|%{myapplogdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{myapp}

# Install server.xml.skel
cp %{SOURCE8} $RPM_BUILD_ROOT%{myappconfdir}/server.xml.skel

# Setup user limits
cp %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/security/limits.d/%{myapp}
sed -i 's|@@SKEL_USER@@|%{myappusername}|g' $RPM_BUILD_ROOT%{_sysconfdir}/security/limits.d/%{myapp}

# Setup Systemd
cp %{SOURCE10} $RPM_BUILD_ROOT%{_systemdir}/%{myapp}.service
sed -i 's|@@SKEL_APP@@|%{myapp}|g' $RPM_BUILD_ROOT%{_systemdir}/%{myapp}.service
sed -i 's|@@SKEL_EXEC@@|%{myappexec}|g' $RPM_BUILD_ROOT%{_systemdir}/%{myapp}.service

# remove uneeded file in RPM
rm -f $RPM_BUILD_ROOT%{myappdir}/*.sh
rm -f $RPM_BUILD_ROOT%{myappdir}/*.bat
rm -f $RPM_BUILD_ROOT%{myappdir}/bin/*.bat
rm -rf $RPM_BUILD_ROOT%{myappdir}/logs
rm -rf $RPM_BUILD_ROOT%{myappdir}/temp
rm -rf $RPM_BUILD_ROOT%{myappdir}/work

# ensure shell scripts are executable
chmod 755 $RPM_BUILD_ROOT%{myappdir}/bin/*.sh

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%if 0%{?suse_version} > 1140
%service_add_pre %{myapp}.service
%endif
# add user and group
%{_sbindir}/groupadd -r -g %{myappgroupid} %{myappusername} 2>/dev/null || :
%{_sbindir}/useradd -s /sbin/nologin -c "%{myapp} user" -g %{myappusername} -r -d %{myappdir} -u %{myappuserid} %{myappusername} 2>/dev/null || :

%post
%if 0%{?suse_version} > 1140
%service_add_post %{myapp}.service
%endif
if [ "$1" == "1" ]; then
  # register app as service
  insserv -f %{myapp}

  # Generated random password for RO and RW accounts
  RANDOMVAL=`echo $RANDOM | md5sum | sed "s| -||g"`
  sed -i "s|@@SKEL_RO_PWD@@|$RANDOMVAL|g" %{_sysconfdir}/sysconfig/%{myapp}
  RANDOMVAL=`echo $RANDOM | md5sum | sed "s| -||g"`
  sed -i "s|@@SKEL_RW_PWD@@|$RANDOMVAL|g" %{_sysconfdir}/sysconfig/%{myapp}

  pushd %{myappdir} >/dev/null
    ln -s %{myapplogdir}  logs
    ln -s %{myapptempdir} temp
    ln -s %{myappworkdir} work
  popd >/dev/null

fi
# Trigger a restart.
#[ -x "/etc/init.d/%{name}" ] && /etc/init.d/%{name} start
# Happy exit even if star script didn't exit cleanly.
#exit 0

%preun
%if 0%{?suse_version} > 1140
%service_del_preun %{myapp}.service
%endif
if [ "$1" == "0" ]; then
  # Uninstall time, stop App and cleanup

  # stop Application
  [ -x "/etc/init.d/%{myapp}" ] && /etc/init.d/%{myapp} stop

  %{_sbindir}/userdel  %{myappusername}
  %{_sbindir}/groupdel %{myappusername}

  rm -rf %{myappworkdir}/* %{myapptempdir}/*

  # unregister app from services
  insserv %{myapp} -r

  # finalize housekeeping
  rm -rf %{myappdir}
  rm -rf %{myapplogdir}
  rm -rf %{myapptempdir}
  rm -rf %{myappworkdir}

fi

%postun
%if 0%{?suse_version} > 1140
%service_del_postun %{myapp}.service
%endif
#if [ $1 -ge 1 ]; then
#    #package upgrade, not uninstall
#fi

# Specific actions in relations with others packages
%triggerin -- otherapp
# Do something if otherapp is installed

%triggerun -- otherapp
# Do something if otherapp is uninstalled


%files
%defattr(-,root,root)
%attr(0755,%{myappusername},%{myappusername}) %dir %{myapplogdir}
%attr(0755, root,root) %{_initrddir}/%{myapp}
%attr(0644,root,root) %{_systemdir}/%{myapp}.service
%config(noreplace) %{_sysconfdir}/sysconfig/%{myapp}
%config %{_sysconfdir}/logrotate.d/%{myapp}
%config %{_sysconfdir}/security/limits.d/%{myapp}
%{myappdir}/bin
%{myappdir}/conf
%{myappdir}/lib
%{myappdir}/webapps
%attr(0755,%{myappusername}, %{myappusername}) %dir %{myappdir}/webapps
%attr(0755,%{myappusername},%{myappusername}) %dir %{myapptempdir}
%attr(0755,%{myappusername},%{myappusername}) %dir %{myappworkdir}
%config(noreplace) %{myappdatadir}/conf
%attr(0755,%{myappusername},%{myappusername}) %dir %{myappdatadir}
%attr(0755,%{myappusername},%{myappusername}) %dir %{myappdatadir}/data
%attr(-,%{myappusername},%{myappusername}) %{myappdatadir}/extensions
%{myappdatadir}/extras
%{myappdatadir}/lib

%doc %{myappdir}/NOTICE
%doc %{myappdir}/RUNNING.txt
%doc %{myappdir}/LICENSE
%doc %{myappdir}/RELEASE-NOTES

%changelog
* Wed Mar 23 2009 henri.gomez@gmail.com 1.0.0-1
- Initial RPM