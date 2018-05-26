import pkg_resources

__VERSION__ = pkg_resources.require("fanboi2")[0].version
__PYRAMID__ = pkg_resources.require("pyramid")[0].version
