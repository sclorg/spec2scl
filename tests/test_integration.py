import pytest
import os

from spec2scl.bin import main


tests_dir = os.path.split(os.path.abspath(__file__))[0]


class TestCli(object):
    """Integration test for the cli command."""

    test_spec_path = '{0}/test_data/test.spec'.format(tests_dir)

    @pytest.mark.parametrize(('args', 'expected_message'), [
        ([test_spec_path, 'foo'], 'You can only convert more specfiles'
         ' using -i (in place) mode.'),
        ([test_spec_path, '-n', '-l foo.txt'], 'argument -l/--list-file:'
         ' not allowed with argument -n/--no-deps-convert'),
    ])
    def test_args_correctly_validated(self, args, expected_message, capsys):
        """Test that CLI arguments are properly validated."""
        with pytest.raises(SystemExit):
            main(args=args)
        out, err = capsys.readouterr()
        assert expected_message in err

    @pytest.mark.parametrize(('args', 'expected_message'), [
        (['foo.spec'], "No such file or directory: 'foo.spec'"),
        ([test_spec_path, '-lfoo.txt'], "No such file or directory: 'foo.txt'"),
    ])
    def test_expected_errors(self, args, expected_message, capsys):
        """Test tht expected errors are properly raised."""
        with pytest.raises(SystemExit):
            main(args=args)
        out, err = capsys.readouterr()
        assert expected_message in out

    @pytest.mark.parametrize(('args', 'in_spec'), [
        ([test_spec_path], ['%{?scl:Requires: %{scl}-runtime}',
                            '{?scl:BuildRequires: %{scl}-runtime}',
                            'Name:           %{?scl_prefix}%{pypi_name}']),
        (['--meta-specfile=foo'], ['%global scl_name_base foo']),
        (['--meta-specfile', 'foo'], ['%global scl_name_base foo']),
        (['--meta-specfile=foo', '-vfoo=bar'], ['export foo=bar']),
    ])
    def test_options_in_spec(self, args, in_spec, capsys):
        """Test that provided options are functional."""
        main(args=args)
        out, err = capsys.readouterr()
        for element in in_spec:
            assert element in out

    @pytest.mark.parametrize(('args', 'not_in_spec'), [
        (['--no-meta-runtime-dep'], '%{?scl:Requires: %{scl}-runtime}'),
        (['--no-meta-buildtime-dep'], '{?scl:BuildRequires: %{scl}-runtime}'),
        (['--skip-functions=handle_name_tag'], 'Name:           %{?scl_prefix}%{pypi_name}'),
    ])
    def test_options_not_in_spec(self, args, not_in_spec, capsys):
        """Test that provided options are functional."""
        main(args=[self.test_spec_path] + args)
        out, err = capsys.readouterr()
        assert not_in_spec not in out

    @pytest.mark.parametrize(('deps_file_content', 'expected_in_spec'), [
        ('python3-devel %{?custom_prefix}\n', '%{?custom_prefix}python3-devel'),
        ('python3-devel\n', '%{?scl_prefix}python3-devel'),
    ])
    def test_supply_list_file(self, deps_file_content, expected_in_spec, tmpdir, capsys):
        """Test --list-file option."""
        deps_file = tmpdir.mkdir("sub").join("deps")
        deps_file.write(deps_file_content)
        main(args=[self.test_spec_path, '--list-file={}'.format(deps_file)])
        out, err = capsys.readouterr()
        assert expected_in_spec in out

    def test_integration(self, capsys):
        """Integration test for converting a test spec file."""
        scl_test_spec_path = '{0}/test_data/scl_test.spec'.format(tests_dir)
        with open(scl_test_spec_path, 'r') as spec_file:
            expected = spec_file.read()
        main(args=[self.test_spec_path])
        out, err = capsys.readouterr()
        assert out == expected
