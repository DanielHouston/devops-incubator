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

# Adjust RPM version (- is not allowed, lowercase strings)
%define rpm_version %(version_rel=`echo %{VERSION} | sed "s/-/./g" | tr "[:upper:]" "[:lower:]"`; echo "$version_rel")

Name:      crash
Version:   %{rpm_version}
Release:   1
Summary:   A shell to extend the Java Platform
Group:     Development/Tools
URL:       http://www.crashub.org/
Packager:  Henri Gomez <henri.gomez@gmail.com>
License:   LGPL
BuildArch: noarch

BuildRoot: %{_tmppath}/build-%{name}-%{version}-%{release}

%define crashdir          /opt/crash

%if 0%{?suse_version}
Requires:           java = 1.6.0
%endif

%if 0%{?fedora} || 0%{?rhel} || 0%{?centos}
Requires:           java = 1:1.6.0
%endif

Source0: crash-%{VERSION}.tar.gz

%description
The Common Reusable SHell (CRaSH) deploys in a Java runtime and provides interactions with the JVM. Commands are written in Groovy and can be developped at runtime making the extension of the shell very easy with fast development cycle

%prep
%setup -q -c

%build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{crashdir}
mkdir -p %{buildroot}%{_bindir}

mv crash-%{VERSION}/crash/* %{buildroot}%{crashdir}
mv crash-%{VERSION}/*.txt %{buildroot}%{crashdir}
cp %{buildroot}%{crashdir}/bin/crash.sh %{buildroot}%{_bindir}

# Set CRASH_HOME
%{__portsed} 's|# Only set|CRASH_HOME="%{crashdir}"\
# Only set|g' %{buildroot}%{_bindir}/crash.sh

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(0755,root,root) %{crashdir}
%attr(0755,root,root) %{_bindir}
%doc %{crashdir}/Readme.txt
%doc %{crashdir}/lgpl-2.1.txt

%changelog
* Wed Mar 27 2013 henri.gomez@gmail.com 1.2.0-cr11-1
- crsh 1.2.0-cr11

* Fri Mar 22 2013 henri.gomez@gmail.com 1.2.0-cr9-1
- crsh 1.2.0-cr9

* Thu Mar 14 2013 henri.gomez@gmail.com 1.2.0-cr7-1
- crsh 1.2.0-cr7

* Fri Mar 1 2013 henri.gomez@gmail.com 1.2.0-cr6-1
- crsh 1.2.0-cr6

* Thu Jan 17 2013 henri.gomez@gmail.com 1.2.0-cr5-1
- crsh 1.2.0-cr5

* Fri Jan 4 2013 henri.gomez@gmail.com 1.2.0-cr3-1
- crsh 1.2.0-cr3

* Fri Jul 20 2012 henri.gomez@gmail.com 1.1.0.rc1-1
- Initial RPM

* Mon Apr 23 2012 henri.gomez@gmail.com 1.0.0-1
- Initial RPM
