"""
Standard input and output services.

Credits:
    The code responsible for dealing with input/output format was copied from
    https://github.com/mattrobenolt/jinja2-cli
    which is licensed under the BSD 2-Clause "Simplified" License.

    Thank you @mattrobenolt!
"""

import sys

from . import Service


class InvalidDataFormat(Exception):
    pass


class InvalidInputData(Exception):
    pass


class MalformedJSON(InvalidInputData):
    pass


class MalformedINI(InvalidInputData):
    pass


class MalformedYAML(InvalidInputData):
    pass


class MalformedQuerystring(InvalidInputData):
    pass


class MalformedToml(InvalidDataFormat):
    pass


class MalformedXML(InvalidDataFormat):
    pass


class MalformedEnv(InvalidDataFormat):
    pass


def get_format(fmt):
    try:
        return formats[fmt]()
    except ImportError:
        raise InvalidDataFormat(fmt)


def get_available_formats():
    for fmt in formats.keys():
        try:
            get_format(fmt)
            yield fmt
        except InvalidDataFormat:
            pass
    yield "auto"


def get_ordered_formats():
    return "yaml", "json", "toml", "ini", "xml", "env", "querystring"


def _load_json():
    try:
        import json

        return json.loads, ValueError, MalformedJSON
    except ImportError:
        import simplejson

        return simplejson.loads, simplejson.decoder.JSONDecodeError, MalformedJSON


def _load_ini():
    try:
        import ConfigParser
    except ImportError:
        import configparser as ConfigParser

    def _parse_ini(data):
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO

        class MyConfigParser(ConfigParser.ConfigParser):
            def as_dict(self):
                d = dict(self._sections)
                for k in d:
                    d[k] = dict(self._defaults, **d[k])
                    d[k].pop("__name__", None)
                return d

        p = MyConfigParser()
        p.read_file(StringIO(data))
        return p.as_dict()

    return _parse_ini, ConfigParser.Error, MalformedINI


def _load_yaml():
    import yaml

    return yaml.load, yaml.YAMLError, MalformedYAML


def _load_querystring():
    try:
        import urlparse
    except ImportError:
        import urllib.parse as urlparse

    def _parse_qs(data):
        """ Extend urlparse to allow objects in dot syntax.
        >>> _parse_qs('user.first_name=Matt&user.last_name=Robenolt')
        {'user': {'first_name': 'Matt', 'last_name': 'Robenolt'}}
        """
        dict_ = {}
        for k, v in urlparse.parse_qs(data).items():
            v = map(lambda x: x.strip(), v)
            v = v[0] if len(v) == 1 else v
            if "." in k:
                pieces = k.split(".")
                cur = dict_
                for idx, piece in enumerate(pieces):
                    if piece not in cur:
                        cur[piece] = {}
                    if idx == len(pieces) - 1:
                        cur[piece] = v
                    cur = cur[piece]
            else:
                dict_[k] = v
        return dict_

    return _parse_qs, Exception, MalformedQuerystring


def _load_toml():
    import toml

    return toml.loads, Exception, MalformedToml


def _load_xml():
    import xml
    import xmltodict

    return xmltodict.parse, xml.parsers.expat.ExpatError, MalformedXML


def _load_env():
    def _parse_env(data):
        """
        Parse an envfile format of key=value pairs that are newline separated
        """
        dict_ = {}
        for line in data.splitlines():
            line = line.lstrip()
            # ignore empty or commented lines
            if not line or line[:1] == "#":
                continue
            k, v = line.split("=", 1)
            dict_[k] = v
        return dict_

    return _parse_env, Exception, MalformedEnv


# Global list of available format parsers on your system
# mapped to the callable/Exception to parse a string into a dict
formats = {
    "json": _load_json,
    "ini": _load_ini,
    "yaml": _load_yaml,
    "yml": _load_yaml,
    "querystring": _load_querystring,
    "toml": _load_toml,
    "xml": _load_xml,
    "env": _load_env,
}


class StandardInputService(Service):
    name = "stdin"

    def read_tasks(self, fmt="auto"):
        stdin = sys.stdin.read()

        if stdin:
            if fmt == "auto":
                for fmt in get_ordered_formats():
                    try:
                        data = self._load_stdin_data(stdin, fmt)
                    except InvalidDataFormat:
                        continue
                    else:
                        break
                else:
                    data = {}
            else:
                data = self._load_stdin_data(stdin, fmt)
        else:
            data = {}

        return data

    @staticmethod
    def _load_stdin_data(stdin, fmt):
        try:
            fn, except_exc, raise_exc = get_format(fmt)
        except InvalidDataFormat:
            if fmt in ("yml", "yaml"):
                raise InvalidDataFormat("%s: install pyyaml to fix" % fmt)
            if fmt == "toml":
                raise InvalidDataFormat("toml: install toml to fix")
            if fmt == "xml":
                raise InvalidDataFormat("xml: install xmltodict to fix")
            raise

        try:
            data = fn(stdin) or {}
        except except_exc:
            raise raise_exc("{} ...".format(stdin[:60]))
        else:
            return data

    def write_tasks(self, tasks, *args, **kwargs):
        raise NotImplementedError


class StandardOutputService(Service):
    name = "stdout"

    def read_tasks(self, *args, **kwargs):
        raise NotImplementedError

    def write_tasks(self, tasks, *args, **kwargs):
        pass
