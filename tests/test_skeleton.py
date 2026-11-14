"""The smallest test: the shared code can be imported. Real tests arrive with each box."""


def test_src_imports():
    import src  # noqa: F401
