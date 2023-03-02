from grblogtools.api import get_dataframe, parse
from grblogtools.plotting import plot

def get_version():
    def get_version_post_py38():
        from importlib.metadata import version  # type: ignore

        return version(__name__)

    def get_version_pre_py38():
        from pkg_resources import get_distribution

        return get_distribution(__name__).version

    def default_version():
        return "unknown"

    for func in (get_version_post_py38, get_version_pre_py38, default_version):
        try:
            return func()
        except Exception:
            pass


__version__ = get_version()