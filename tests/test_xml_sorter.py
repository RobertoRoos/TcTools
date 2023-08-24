import pytest

import tctools.xml_sort

from .conftest import assert_order_of_lines_in_file


def test_help(capsys):
    """Test the help text."""

    with pytest.raises(SystemExit) as err:
        tctools.xml_sort.main("--help")

    assert err.type == SystemExit

    message = capsys.readouterr().out
    assert "usage:" in message and "options:" in message


def test_single_file_plain_xml(plc_code):
    """Test how a plain XML file gets sorted."""
    file = plc_code / "plant_catalog.xml"

    expected = [
        "<AVAILABILITY>010299</AVAILABILITY>",
        "<AVAILABILITY>012099</AVAILABILITY>",
        "<AVAILABILITY>012699</AVAILABILITY>",
        "<AVAILABILITY>020199</AVAILABILITY>",
        "<AVAILABILITY>030699</AVAILABILITY>",
        "<AVAILABILITY>030699</AVAILABILITY>",
        "<AVAILABILITY>031599</AVAILABILITY>",
        "<AVAILABILITY>041899</AVAILABILITY>",
        "<AVAILABILITY>051799</AVAILABILITY>",
    ]

    assert_order_of_lines_in_file(expected, file, is_substring=True, check_true=False)
    tctools.xml_sort.main(str(file))
    assert_order_of_lines_in_file(expected, file, is_substring=True)


def test_use_attributes(plc_code):
    """Test how attributes are used to sort nodes."""
    file = plc_code / "books.xml"

    expected = [
        '<book letter="a">',
        '<book letter="b">',
        '<book letter="c">',
    ]
    # <name>*</name> is not used for sorting

    assert_order_of_lines_in_file(expected, file, is_substring=True, check_true=False)
    tctools.xml_sort.main(str(file))
    assert_order_of_lines_in_file(expected, file, is_substring=True)


def test_single_file_dry(plc_code, capsys):
    """Test using dry run."""
    file = plc_code / "books.xml"

    tctools.xml_sort.main(str(file), "--dry")

    result = capsys.readouterr().out
    assert '<book letter="a">' in result

    tctools.xml_sort.main(str(file))  # Make change for real
    capsys.readouterr()

    tctools.xml_sort.main(str(file), "--dry")

    result3 = capsys.readouterr().out
    assert '<book letter="a">' not in result3
    assert "identical" in result3


def test_single_file_check(plc_code):
    """Test using check flag."""
    file = plc_code / "books.xml"

    code = tctools.xml_sort.main(str(file), "--check")
    assert code != 0

    tctools.xml_sort.main(str(file))  # Make change for real

    code2 = tctools.xml_sort.main(str(file), "--check")
    assert code2 == 0


def test_single_project_file(plc_code):
    """Test XML sort on a single target file."""
    file = plc_code / "TwinCAT Project1" / "TwinCAT Project1.tsproj"
    tctools.xml_sort.main(
        str(file),
        "--skip-nodes",
        "Device",
        "DeploymentEvents",
        "TcSmItem",
        "DataType",
    )


def test_multiple_files(plc_code, caplog):
    """Test CLI interface."""
    file1 = plc_code / "books.xml"
    file2 = plc_code / "plant_catalog.xml"
    tctools.xml_sort.main(str(file1), str(file2), "-l", "DEBUG")
    result = "\n".join([rec.msg for rec in caplog.records])
    assert "books.xml" in result
    assert "plant_catalog.xml" in result


def test_folder(plc_code, caplog):
    """Test CLI interface."""
    tctools.xml_sort.main(str(plc_code), "--filter", "*.xml", "-l", "DEBUG")
    result = "\n".join([rec.msg for rec in caplog.records])
    assert "books.xml" in result
    assert "plant_catalog.xml" in result


def test_project(plc_code, caplog):
    """Test running over a full project as normal."""
    file = plc_code / "TwinCAT Project1"
    tctools.xml_sort.main(
        str(file),
        "-r",
        "--skip-nodes",
        "Device",
        "DeploymentEvents",
        "TcSmItem",
        "DataType",
        "-r",
        "--filter",
        "*.tsproj",
        "*.xti",
        "*.plcproj",
        "-l",
        "DEBUG",
    )

    result = "\n".join([rec.msg for rec in caplog.records])

    expected = [
        "TwinCAT Project1.tsproj",
        "MyPlc.plcproj",
        "Device 2 (EtherCAT).xti",
        "NC.xti",
    ]

    for exp in expected:
        assert exp in result
