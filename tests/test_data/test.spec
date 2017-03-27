%global pypi_name spec2scl

Name:           %{pypi_name}
Version:        1.1.4
Release:        1%{?dist}
Summary:        Convert RPM specfiles to be SCL ready

License:        MIT
URL:            https://github.com/sclorg/spec2scl
Source0:        https://files.pythonhosted.org/packages/source/s/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
 
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%if 0%{?fedora}
BuildRequires:  python3-flexmock
BuildRequires:  python3-jinja2
BuildRequires:  python3-pytest
%endif

Requires:       python3-setuptools
Requires:       python3-jinja2

%description
spec2scl is a tool to convert RPM specfiles to SCL-style specfiles.

%prep
%setup -q -n %{pypi_name}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --skip-build --root %{buildroot}

%check
%if 0%{?fedora}
PYTHONPATH=$(pwd) py.test-%{python3_version}
%endif

%files
%doc README.rst
%license LICENSE
%{_bindir}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info

%changelog
* Thu Feb 16 2017 John Doe <john@doe.com> - 1.1.4-1
- Update
