import sys


def test_python_version():
    """Python 3 is required to run this code."""
    system_major = sys.version_info.major

    if not system_major == 3:
        raise AssertionError()
