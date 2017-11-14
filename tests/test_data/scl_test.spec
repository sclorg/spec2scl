%{?scl:%scl_package %{pypi_name}}
%{!?scl:%global pkg_name %{name}}

%global pypi_name spec2scl

Name:           %{?scl_prefix}%{pypi_name}
Version:        1.1.4
Release:        1%{?dist}
Summary:        Convert RPM specfiles to be SCL ready

License:        MIT
URL:            https://github.com/sclorg/spec2scl
Source0:        https://files.pythonhosted.org/packages/source/s/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
 
%{?scl:Requires: %{scl}-runtime}
%{?scl:BuildRequires: %{scl}-runtime}
BuildRequires:  %{?scl_prefix}python3-devel
BuildRequires:  %{?scl_prefix}python3-setuptools

%if 0%{?fedora}
BuildRequires:  %{?scl_prefix}python3-flexmock
BuildRequires:  %{?scl_prefix}python3-jinja2
BuildRequires:  %{?scl_prefix}python3-pytest
%endif

Requires:       %{?scl_prefix}python3-setuptools
Requires:       %{?scl_prefix}python3-jinja2

# Scriptlet-specific requirements
Requires(pre):  %{?scl_prefix}some-package
Requires(post): %{?scl_prefix}some-package


%description
spec2scl is a tool to convert RPM specfiles to SCL-style specfiles.


%prep
%{?scl:scl enable %{scl} - << \EOF}
set -ex
%setup -q -n %{pypi_name}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info
%{?scl:EOF}


%build
%{?scl:scl enable %{scl} - << \EOF}
set -ex
%{__python3} setup.py build
%{?scl:EOF}


%install
%{?scl:scl enable %{scl} - << \EOF}
set -ex
%{__python3} setup.py install --skip-build --root %{buildroot}
%{?scl:EOF}


%check
%{?scl:scl enable %{scl} - << \EOF}
set -ex
%if 0%{?fedora}
PYTHONPATH=$(pwd) py.test-%{python3_version}
%endif
%{?scl:EOF}


%files
%doc README.rst
%license LICENSE
%{_bindir}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info


%changelog
* Thu Feb 16 2017 John Doe <john@doe.com> - 1.1.4-1
- Update
