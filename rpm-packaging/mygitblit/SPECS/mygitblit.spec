# Avoid unnecessary debug-information (native code)
%define		debug_package %{nil}

# Avoid jar repack (brp-java-repack-jars)
#%define __jar_repack 0

# Avoid CentOS 5/6 extras processes on contents (especially brp-java-repack-jars)
%define __os_install_post %{nil}

%ifos darwin
%define __portsed sed -i "" -e
%else
%define __portsed sed -i
%endif

%if 0%{?TOMCAT_REL:1}
%define tomcat_rel        %{TOMCAT_REL}
%else
%define tomcat_rel        7.0.57
%endif

%if 0%{?GITBLIT_REL:1}
%define gitblit_rel    %{GITBLIT_REL}
%else
%define gitblit_rel    1.6.2
%endif

Name: mygitblit
Version: %{gitblit_rel}
Release: 2
Summary: GitBlit %{gitblit_rel} powered by Apache Tomcat %{tomcat_rel}
Group: Development/Tools/Version Control
URL: http://gitblit.com/
Vendor: devops-incubator
License: Apache-2.0
BuildArch:  noarch

%define appname         mygitblit
%define appusername     mygitblt
%define appuserid       1238
%define appgroupid      1238

%define appdir          /opt/%{appname}
%define appdatadir      %{_var}/lib/%{appname}
%define applogdir       %{_var}/log/%{appname}
%define appexec         %{appdir}/bin/catalina.sh
%define appconfdir      %{appdir}/conf
%define appconflocaldir %{appdir}/conf/Catalina/localhost
%define appwebappdir    %{appdir}/webapps

%if 0%{?suse_version} >= 1320
%define apptempdir        /run/%{appname}
%else
%define apptempdir        %{_var}/run/%{appname}
%endif

%define appworkdir      %{_var}/spool/%{appname}
%define appcron         %{appdir}/bin/cron.sh

%define _cronddir       %{_sysconfdir}/cron.d
%define _initrddir      %{_sysconfdir}/init.d
%define _systemddir     /lib/systemd
%define _systemdir      %{_systemddir}/system

%if 0%{?fedora} || 0%{?rhel} || 0%{?centos} || 0%{?suse_version} < 1200
%define servicestart %{_initrddir}/%{appname} start
%define servicestop  %{_initrddir}/%{appname} stop
%define serviceon    chkconfig %{appname} on
%define serviceoff   chkconfig %{appname} off
%else
%define servicestart service %{appname} start
%define servicestop  service %{appname} stop
%define serviceon    systemctl enable %{appname}
%define serviceoff   systemctl disable %{appname} 
%endif

BuildRoot: %{_tmppath}/build-%{name}-%{version}-%{release}

%if 0%{?suse_version} > 1140
BuildRequires: systemd
%{?systemd_requires}
%else
%define systemd_requires %{nil}
%endif

%if 0%{?suse_version} > 1000
PreReq: %fillup_prereq
%endif

%if 0%{?suse_version}
Requires: cron
Requires: logrotate
%endif

%if 0%{?suse_version}
Requires:           java >= 1.6.0
%endif

%if 0%{?fedora} || 0%{?rhel} || 0%{?centos}
Requires:           java >= 1:1.6.0
%endif

Requires(pre):      %{_sbindir}/groupadd
Requires(pre):      %{_sbindir}/useradd

Source0: http://archive.apache.org/dist/tomcat/tomcat-7/v%{tomcat_rel}/bin/apache-tomcat-%{tomcat_rel}.tar.gz
Source1: http://dl.bintray.com/gitblit/releases/gitblit-%{gitblit_rel}.war
Source2: initd.skel
Source3: sysconfig.skel
Source4: jmxremote.access.skel
Source5: jmxremote.password.skel
Source6: setenv.sh.skel
Source7: logrotate.skel
Source8: server.xml.skel
Source9: limits.conf.skel
Source10: systemd.skel
Source11: http://archive.apache.org/dist/tomcat/tomcat-7/v%{tomcat_rel}/bin/extras/catalina-jmx-remote-%{tomcat_rel}.jar
Source12: context.xml.skel
Source13: logging.properties.skel
Source14: crond.skel
Source15: cron.sh.skel

%description
Gitblit is an open-source, pure Java stack for managing, viewing, and serving Git repositories.
It's designed primarily as a tool for small workgroups who want to host centralized repositories
This package contains Gitblit %{gitblit_rel} powered by Apache Tomcat %{tomcat_rel}

%prep
%setup -q -c

%build

%install
# Prep the install location.
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_cronddir}
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
mkdir -p %{buildroot}%{_sysconfdir}/security/limits.d
mkdir -p %{buildroot}%{_systemdir}

mkdir -p %{buildroot}%{appdir}
mkdir -p %{buildroot}%{appdatadir}

mkdir -p %{buildroot}%{applogdir}
mkdir -p %{buildroot}%{apptempdir}
mkdir -p %{buildroot}%{appworkdir}

# Copy tomcat
mv apache-tomcat-%{tomcat_rel}/* %{buildroot}%{appdir}

# Create conf/Catalina/localhost
mkdir -p %{buildroot}%{appconflocaldir}

# remove default webapps
rm -rf %{buildroot}%{appdir}/webapps/*

# patches to have logs under /var/log/app
# remove manager and host-manager logs (via .skel file)
cp %{SOURCE13} %{buildroot}%{appdir}/conf/logging.properties
%{__portsed} 's|\${catalina.base}/logs|%{applogdir}|g' %{buildroot}%{appdir}/conf/logging.properties

# appname webapp is ROOT.war (will respond to /)
cp %{SOURCE1}  %{buildroot}%{appwebappdir}/ROOT.war

# init.d
cp  %{SOURCE2} %{buildroot}%{_initrddir}/%{appname}
%{__portsed} 's|@@MYAPP_APP@@|%{appname}|g' %{buildroot}%{_initrddir}/%{appname}
%{__portsed} 's|@@MYAPP_USER@@|%{appusername}|g' %{buildroot}%{_initrddir}/%{appname}
%{__portsed} 's|@@MYAPP_VERSION@@|version %{version} release %{release}|g' %{buildroot}%{_initrddir}/%{appname}
%{__portsed} 's|@@MYAPP_EXEC@@|%{appexec}|g' %{buildroot}%{_initrddir}/%{appname}
%{__portsed} 's|@@MYAPP_DATADIR@@|%{appdatadir}|g' %{buildroot}%{_initrddir}/%{appname}
%{__portsed} 's|@@MYAPP_LOGDIR@@|%{applogdir}|g' %{buildroot}%{_initrddir}/%{appname}
%{__portsed} 's|@@MYAPP_TMPDIR@@|%{apptempdir}|g' %{buildroot}%{_initrddir}/%{appname}

# sysconfig
cp  %{SOURCE3}  %{buildroot}%{_sysconfdir}/sysconfig/%{appname}
%{__portsed} 's|@@MYAPP_APP@@|%{appname}|g' %{buildroot}%{_sysconfdir}/sysconfig/%{appname}
%{__portsed} 's|@@MYAPP_APPDIR@@|%{appdir}|g' %{buildroot}%{_sysconfdir}/sysconfig/%{appname}
%{__portsed} 's|@@MYAPP_DATADIR@@|%{appdatadir}|g' %{buildroot}%{_sysconfdir}/sysconfig/%{appname}
%{__portsed} 's|@@MYAPP_LOGDIR@@|%{applogdir}|g' %{buildroot}%{_sysconfdir}/sysconfig/%{appname}
%{__portsed} 's|@@MYAPP_USER@@|%{appusername}|g' %{buildroot}%{_sysconfdir}/sysconfig/%{appname}
%{__portsed} 's|@@MYAPP_CONFDIR@@|%{appconfdir}|g' %{buildroot}%{_sysconfdir}/sysconfig/%{appname}

%if 0%{?suse_version} > 1000
mkdir -p %{buildroot}%{_var}/adm/fillup-templates
mv %{buildroot}%{_sysconfdir}/sysconfig/%{appname} %{buildroot}%{_var}/adm/fillup-templates/sysconfig.%{appname}
%endif

# JMX (including JMX Remote)
cp %{SOURCE11} %{buildroot}%{appdir}/lib
cp %{SOURCE4}  %{buildroot}%{appconfdir}/jmxremote.access.skel
cp %{SOURCE5}  %{buildroot}%{appconfdir}/jmxremote.password.skel

# Our custom setenv.sh to get back env variables
cp  %{SOURCE6} %{buildroot}%{appdir}/bin/setenv.sh
%{__portsed} 's|@@MYAPP_APP@@|%{appname}|g' %{buildroot}%{appdir}/bin/setenv.sh

# Install logrotate
cp %{SOURCE7} %{buildroot}%{_sysconfdir}/logrotate.d/%{appname}
%{__portsed} 's|@@MYAPP_LOGDIR@@|%{applogdir}|g' %{buildroot}%{_sysconfdir}/logrotate.d/%{appname}

# Install server.xml.skel
cp %{SOURCE8} %{buildroot}%{appconfdir}/server.xml.skel

# Setup user limits
cp %{SOURCE9} %{buildroot}%{_sysconfdir}/security/limits.d/%{appname}.conf
%{__portsed} 's|@@MYAPP_USER@@|%{appusername}|g' %{buildroot}%{_sysconfdir}/security/limits.d/%{appname}.conf

%if 0%{?suse_version} > 1140
# Setup Systemd
cp %{SOURCE10} %{buildroot}%{_systemdir}/%{appname}.service
%{__portsed} 's|@@MYAPP_APP@@|%{appname}|g' %{buildroot}%{_systemdir}/%{appname}.service
%{__portsed} 's|@@MYAPP_EXEC@@|%{appexec}|g' %{buildroot}%{_systemdir}/%{appname}.service
%endif

# Install context.xml (override previous one)
cp %{SOURCE12} %{buildroot}%{appconfdir}/context.xml.skel
%{__portsed} 's|@@MYAPP_DATADIR@@|%{appdatadir}|g' %{buildroot}%{appconfdir}/context.xml.skel

# Setup cron.d
cp %{SOURCE14} %{buildroot}%{_cronddir}/%{appname}
%{__portsed} 's|@@MYAPP_APP@@|%{appname}|g' %{buildroot}%{_cronddir}/%{appname}
%{__portsed} 's|@@MYAPP_CRON@@|%{appcron}|g' %{buildroot}%{_cronddir}/%{appname}
%{__portsed} 's|@@MYAPP_USER@@|%{appusername}|g' %{buildroot}%{_cronddir}/%{appname}

# Setup cron.sh
cp %{SOURCE15} %{buildroot}%{appcron}
%{__portsed} 's|@@MYAPP_APP@@|%{appname}|g' %{buildroot}%{appcron}
%{__portsed} 's|@@MYAPP_LOGDIR@@|%{applogdir}|g' %{buildroot}%{appcron}
%{__portsed} 's|@@MYAPP_USER@@|%{appusername}|g' %{buildroot}%{appcron}

# remove uneeded file in RPM
rm -f %{buildroot}%{appdir}/*.sh
rm -f %{buildroot}%{appdir}/*.bat
rm -f %{buildroot}%{appdir}/bin/*.bat
rm -rf %{buildroot}%{appdir}/logs
rm -rf %{buildroot}%{appdir}/temp
rm -rf %{buildroot}%{appdir}/work

# ensure shell scripts are executable
chmod 755 %{buildroot}%{appdir}/bin/*.sh

%clean
rm -rf %{buildroot}

%pre
%if 0%{?suse_version} > 1140
%service_add_pre %{appname}.service
%endif
# First install time, add user and group
if [ "$1" == "1" ]; then
  %{_sbindir}/groupadd -r -g %{appgroupid} %{appusername} 2>/dev/null || :
  %{_sbindir}/useradd -s /sbin/nologin -c "%{appname} user" -g %{appusername} -r -d %{appdatadir} -u %{appuserid} %{appusername} 2>/dev/null || :
else
# Update time, stop service if running
  if [ "$1" == "2" ]; then
    if [ -f %{_var}/run/%{appname}.pid ]; then
      %{servicestop}
      touch %{applogdir}/rpm-update-stop
    fi
    # clean up deployed webapp
    rm -rf %{appwebappdir}/ROOT
    # clean up Tomcat workdir 
    rm -rf %{appworkdir}/Catalina
  fi
fi

%post
%if 0%{?suse_version} > 1140
%service_add_post %{appname}.service
%endif
%if 0%{?suse_version} > 1000
%fillup_only
%endif

# First install time, register service, generate random passwords and start application
if [ "$1" == "1" ]; then
  # register app as service
  %{serviceon}

  # Generated random password for RO and RW accounts
  if [ -f %{_sysconfdir}/sysconfig/%{appname} ]; then
    RANDOMVAL=`echo $RANDOM | md5sum | sed "s| -||g" | tr -d " "`
    %{__portsed} "s|@@MYAPP_RO_PWD@@|$RANDOMVAL|g" %{_sysconfdir}/sysconfig/%{appname}
    RANDOMVAL=`echo $RANDOM | md5sum | sed "s| -||g" | tr -d " "`
    %{__portsed} "s|@@MYAPP_RW_PWD@@|$RANDOMVAL|g" %{_sysconfdir}/sysconfig/%{appname}
  fi
  
  pushd %{appdir} >/dev/null
  ln -s %{applogdir}  logs
  ln -s %{apptempdir} temp
  ln -s %{appworkdir} work
  popd >/dev/null

  # start application at first install (uncomment next line this behaviour not expected)
  # %{servicestart}
else
  # Update time, restart application if it was running
  if [ "$1" == "2" ]; then
    if [ -f %{applogdir}/rpm-update-stop ]; then
      # restart application after update (comment next line this behaviour not expected)
      %{servicestart}
      rm -f %{applogdir}/rpm-update-stop
    fi
  fi
fi

%preun
%if 0%{?suse_version} > 1140
%service_del_preun %{appname}.service
%endif
if [ "$1" == "0" ]; then
  # Uninstall time, stop service and cleanup

  # stop service
  %{servicestop}

  # unregister app from services
  %{serviceoff}

  # finalize housekeeping
  rm -rf %{appdir}
  rm -rf %{applogdir}
  rm -rf %{apptempdir}
  rm -rf %{appworkdir}
fi

%postun
%if 0%{?suse_version} > 1140
%service_del_postun %{appname}.service
%endif
if [ "$1" == "0" ]; then
  if [ -d %{appwebappdir}/ROOT ]; then 
    rm -rf %{appwebappdir}/ROOT
  fi
fi

%files
%defattr(-,root,root)
%dir %{appdir}
%attr(0755,%{appusername},%{appusername}) %dir %{applogdir}
%attr(0755, root,root) %{_initrddir}/%{appname}

%if 0%{?suse_version} > 1140
%dir %{_systemddir}
%dir %{_systemdir}
%attr(0644,root,root) %{_systemdir}/%{appname}.service
%endif

%if 0%{?suse_version} > 1000
%{_var}/adm/fillup-templates/sysconfig.%{appname}
%else
%dir %{_sysconfdir}/sysconfig
%config(noreplace) %{_sysconfdir}/sysconfig/%{appname}
%endif

%config %{_sysconfdir}/logrotate.d/%{appname}
%dir %{_sysconfdir}/security/limits.d
%config %{_sysconfdir}/security/limits.d/%{appname}.conf
%config %{_cronddir}/%{appname}
%{appdir}/bin
%{appdir}/conf
%{appdir}/lib
%attr(-,%{appusername}, %{appusername}) %{appdir}/webapps
%attr(0755,%{appusername},%{appusername}) %dir %{appconflocaldir}
%attr(0755,%{appusername},%{appusername}) %dir %{appdatadir}
%ghost %{apptempdir}
%attr(0755,%{appusername},%{appusername}) %dir %{appworkdir}
%doc %{appdir}/NOTICE
%doc %{appdir}/RUNNING.txt
%doc %{appdir}/LICENSE
%doc %{appdir}/RELEASE-NOTES

%changelog
* Sun Nov 23 2014 henri.gomez@gmail.com 1.6.2-2
- Update Tomcat to 7.0.57

* Tue Oct 28 2014 henri.gomez@gmail.com 1.6.2-1
- GitBlit 1.6.2

* Tue Oct 21 2014 henri.gomez@gmail.com 1.6.0-1
- GitBlit 1.6.1

* Thu Jun 19 2014 henri.gomez@gmail.com 1.5.0-1
- GitBlit 1.5.0
- Update Tomcat to 7.0.54

* Mon Mar 24 2014 henri.gomez@gmail.com 1.4.1-1
- GitBlit 1.4.1
- Update download URL (bintray)

* Sat Mar 1 2014 hgomez@gmail.com 1.3.2-6
- Update Tomcat to 7.0.52

* Tue Jan 21 2014 drautureau@gmail.com 1.3.2-5
- Fix sysconfig

* Mon Jan 13 2014 henri.gomez@gmail.com 1.3.2-4
- Update Tomcat to 7.0.50

* Wed Dec 18 2013 henri.gomez@gmail.com 1.3.2-3
- Fix typo in seding init.d tempdir

* Sun Oct 27 2013 henri.gomez@gmail.com 1.3.2-2
- Update Tomcat to 7.0.47
- Move to OBS

* Wed Sep 18 2013 henri.gomez@gmail.com 1.3.2-1
- GitBlit 1.3.2

* Tue Aug 20 2013 henri.gomez@gmail.com 1.3.1-1
- GitBlit 1.3.1

* Mon Jul 8 2013 henri.gomez@gmail.com 1.2.1-7
- Apache Tomcat 7.0.42 released
- Use %ghost directive for /var/run contents (rpmlint)
- cron contents should be marked as %config (rpmlint)
- cron/logrotate required for SUSE (rpmlint)

* Wed Jun 12 2013 henri.gomez@gmail.com 1.2.1-6
- Apache Tomcat 7.0.41 released, update package

* Fri May 17 2013 henri.gomez@gmail.com 1.2.1-5
- Apache Tomcat 7.0.40 released, update package

* Tue Apr 9 2013 henri.gomez@gmail.com 1.2.1-4
- Simplify logrotate
- Use cron for housekeeping
- Move temp contents to /var/run/myartifactory
- Move work contents to /var/spool/myartifactory

* Mon Feb 18 2013 henri.gomez@gmail.com 1.2.1-3
- Apache Tomcat 7.0.37 released, update package

* Fri Feb 1 2013 henri.gomez@gmail.com 1.2.1-2
- Use startproc instead of start_daemon to ensure userid is not overrided 

* Fri Jan 17 2013 henri.gomez@gmail.com 1.2.1-1
- Update to GitBlit 1.2.1
- credentials are now under %{appdatadir}/conf/users.conf

* Thu Jan 17 2013 henri.gomez@gmail.com 1.2.0-2
- Apache Tomcat 7.0.35 released, update package

* Fri Jan 11 2013 henri.gomez@gmail.com 1.2.0-1
- Update to GitBlit 1.2.0 

* Tue Dec 19 2012 henri.gomez@gmail.com 1.1.0-4
- Update to Apache Tomcat 7.0.34

* Fri Oct 12 2012 henri.gomez@gmail.com 1.1.0-3
- Update to Apache Tomcat 7.0.32

* Wed Oct 3 2012 henri.gomez@gmail.com 1.1.0-2
- Reduce number of log files (manager and host-manager)

* Fri Sep 28 2012 henri.gomez@gmail.com 1.1.0-1
- Update to Apache Tomcat 7.0.30
- Update to GitBlit 1.1.0

* Mon Aug 20 2012 henri.gomez@gmail.com 1.0.0-3
- Remove duplicate JMX settings definition

* Thu Jul 19 2012 henri.gomez@gmail.com 1.0.0-2
- Rework WEB-INF properties injection in init.d using context.xml.skel
- Add missing subdir scripts and grape
- Update ownership of conf directory

* Mon Jul 16 2012 henri.gomez@gmail.com 1.0.0-1
- Update to GitBlit 1.0.0

* Wed Jul 11 2012 henri.gomez@gmail.com 0.9.3-3
- Update to Tomcat 7.0.29

* Wed Jun 20 2012 henri.gomez@gmail.com 0.9.3-2
- Update to Tomcat 7.0.28

* Wed Apr 25 2012 henri.gomez@gmail.com 0.9.3-1
- Update to GitBlit 0.9.3 

* Wed Mar 7 2012 henri.gomez@gmail.com 0.8.2-0
- Distribution dependant Requires for Java

* Fri Jan 6 2012 henri.gomez@gmail.com 0.8.1-1
- Create conf/Catalina/localhost with user rights

* Sat Dec 3 2011 henri.gomez@gmail.com 0.8.1-0
- Initial RPM
