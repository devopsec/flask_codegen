import sys, linecache, json
from datetime import datetime, date, time
from decimal import Decimal
from types import MethodType
from collections import Iterable
from inspect import getfullargspec
from sqlalchemy.ext.declarative import DeclarativeMeta

class ColorPrint():
    @staticmethod
    def err(message, end = '\n'):
        print('\x1b[1;31m' + str(message).strip() + '\x1b[0m' + end)

    @staticmethod
    def pas(message, end = '\n'):
        print('\x1b[1;32m' + str(message).strip() + '\x1b[0m' + end)

    @staticmethod
    def warn(message, end = '\n'):
        print('\x1b[1;33m' + str(message).strip() + '\x1b[0m' + end)

    @staticmethod
    def inf(message, end = '\n'):
        print('\x1b[1;34m' + str(message).strip() + '\x1b[0m' + end)

    @staticmethod
    def bold(message, end = '\n'):
        print('\x1b[1;37m' + str(message).strip() + '\x1b[0m' + end)

def print_exception():
    """ debugging of an exception """
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    ColorPrint.err('( BACKTRACE ):\n[FILE]: {}\n[LINE NUM]: {}\n[FUNCTION]: {}\n[EXCEPTION]: {}'.format(filename, lineno, line.strip(), exc_obj))

def datetime_encode(x):
    return datetime.strftime(x, '%Y-%m-%d %H:%M:%S')

def date_encode(x):
    return datetime.strftime(x, '%Y-%m-%d')

def time_encode(x):
    return datetime.strftime(x, '%H:%M:%S')

def datetime_decode(x):
    return datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

def date_decode(x):
    return datetime.strptime(x, '%Y-%m-%d')

def time_decode(x):
    return datetime.strptime(x, '%H:%M:%S')

def isjson_str(json_str):
    """
    Determine if json_str is a proper JSON formatted str
    :param json_str: a possible JSON string
    :return: True | False
    """
    try:
        json_object = json.loads(json_str)
    except Exception:
        return False
    return True

def isjson_dict(json_dict):
    """
    Determine if json_dict is a proper JSON dict
    :param json_dict: a possible JSON formatted dict
    :return: True | False
    """
    try:
        json_object = json.dumps(json_dict)
    except Exception:
        return False
    return True

def get_class_by_tablename(tablename, Base):
  """
  Return class reference mapped to table.
  :param tablename: String with name of table
  :param Base: The declarative base for that table
  :return: Class reference or None.
  """
  for c in Base._decl_class_registry.values():
    if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
      return c

def json_decode(data, cls=None):
    """  deserialize json formatted str into json object (dicts / lists)"""
    try:
        if not cls is None:
            return json.dumps(data, cls=cls)
        return json.loads(data)
    except:
        raise ValueError('Malformed JSON')

def json_encode(data, cls=None):
    """ serialize json object (dicts / lists) into json formatted str """
    try:
        if not cls is None:
            return json.dumps(data, cls=cls)
        return json.dumps(data)
    except:
        raise ValueError('Malformed JSON')

def pprint_json(data):
    """ works on lists or dicts """
    if isinstance(data, list):
        data = dict(data=data)
    print(json.dumps(data, sort_keys=True, indent=4))


class AlchemyEncoder(json.JSONEncoder):
    """ JSON serializer for objects not serializable by default json code """

    simple_types = (int, str, float, bytes, bool, type(None))

    def __init__(self, revisit_self=False, fields_to_expand=[], check_circular=False, sort_keys=None, indent=None,
                 allow_nan=True, skipkeys=False, ensure_ascii=True, separators=None, default=None):
        """ Extend superclass __init__ to add params """

        super().__init__(skipkeys, ensure_ascii, check_circular, allow_nan, sort_keys, indent, separators, default)
        self.revisit_self = revisit_self
        self.fields_to_expand = fields_to_expand
        self.visited_values = []

    def default(self, value):
        """ Override JSONEcoder default class """

        if self.is_valid_callable(value):
            value = value()

        if isinstance(value, self.simple_types):
            return value

        elif isinstance(value, Decimal):
            return

        elif isinstance(value, datetime):
            return self.serialize_datetime(value)

        elif isinstance(value, date):
            return self.serialize_date(value)

        elif isinstance(value, time):
            return self.serialize_time(value)

        elif isinstance(value, dict):
            return self.serialize_dict(value)

        elif isinstance(value, list):
            return self.serialize_list(value)

        elif isinstance(value, Iterable):
            return self.serialize_iter(value)

        elif isinstance(value.__class__, DeclarativeMeta):
            return self.serialize_model(value)

        else:
            return json.JSONEncoder.default(self, value)

    @staticmethod
    def is_valid_callable(func):
        if callable(func):
            i = getfullargspec(func)
            if i.args == ['self'] and isinstance(func, MethodType) and not any([i.varargs, i.varkw]):
                return True
            return not any([i.args, i.varargs, i.varkw])
        return False

    def serialize_model(self, value):
        # don't re-visit self
        if self.revisit_self:
            if value in self.visited_values:
                return None
            self.visited_values.append(value)

        # go through each field in this SQLalchemy class
        fields = {}
        for field in [x for x in dir(value) if not x.startswith('_') and x != 'metadata']:
            val = value.__getattribute__(field)

            # is this field another SQLalchemy valueect, or a list of SQLalchemy valueects?
            if isinstance(val.__class__, DeclarativeMeta) or (
                    isinstance(val, list) and len(val) > 0 and isinstance(val[0].__class__, DeclarativeMeta)):
                # unless we're expanding this field, stop here
                if field not in self.fields_to_expand:
                    # not expanding this field: set it to None and continue
                    fields[field] = None
                    continue

            elif isinstance(val, (datetime, date)):
                val =  val.isoformat()

            fields[field] = val
        # a json-encodable dict
        return fields

    def serialize_decimal(self, value):
        value.to_eng_string()

    def serialize_datetime(self, value):
        return value.strftime('%Y-%m-%d %H:%M:%S')

    def serialize_date(self, value):
        return value.strftime('%Y-%m-%d')

    def serialize_time(self, value):
        return value.strftime('%H:%M:%S')

    def serialize_iter(self, value):
        res = []
        for v in value:
            res.append(self.default(value=v))
        return res

    def serialize_list(self, value):
        self.serialize_iter(value=value)

    def serialize_dict(self, value):
        res = {}
        for k, v in value.items():
            res[k] = self.default(value=v)
        return res


