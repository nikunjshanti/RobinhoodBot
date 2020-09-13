from collections import Sequence
from itertools import chain, count
import json

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict


class DefaultOrderedDict(OrderedDict):
    def __missing__(self, key):
        self[key] = type(self)()
        return self[key]


class AutoDict(dict):
    def __missing__(self, k):
        self[k] = AutoDict()
        return self[k]

def returnpythonobject(jsonstring):
    return ast.literal_eval(jsonstring)


def depth(seq):
    for level in count():
        if not seq:
            return level
        seq = list(chain.from_iterable(s for s in seq if isinstance(s, Sequence)))

def find_keyvalues_json(keyname, valuename, jsonobj):
    results = []

    def _decode_dict(a_dict):
        try:
            #print json.dumps(a_dict)
            for key,value in a_dict.items():
                if key ==keyname and value == valuename:
                    results.append(a_dict)
        except KeyError:
            pass
        return a_dict

    json.loads(json.dumps(jsonobj), object_hook=_decode_dict)  # return value ignored
    return results


def find_values_json(id, jsonobj):
    results = []

    def _decode_dict(a_dict):
        try: results.append(a_dict[id])
        except KeyError: pass
        return a_dict

    json.loads(json.dumps(jsonobj), object_hook=_decode_dict)  # return value ignored
    return results

def nested_item(depth, value):
    if depth <= 1:
        return [value]
    else:
        return [nested_item(depth - 1, value)]

def flatten(lis):
    """Given a list, possibly nested to any level, return it flattened."""
    new_lis = []
    for item in lis:
        if type(item) == type([]):
            new_lis.extend(flatten(item))
        else:
            new_lis.append(item)
    return new_lis


def remove_from_dict_in_list(l, k):
    for i in l:
        if isinstance(i, list):
            remove_from_dict_in_list(i, k)
        elif isinstance(i, dict):
            remove_entries(i, k)

def remove_entries_fromdict_usinglist(d, k: list):
    for item in k:
        try:
            del(d[item])
        except KeyError:
            pass

    return d

def remove_entries(d, k):
    if k in d:
        del d[k]
    for value in d.values():
        if isinstance(value, dict):
            remove_entries(value, k)
        elif isinstance(value, list):
            remove_from_dict_in_list(value, k)

def remove_listitems(orglist : list, itemslist : list):

    for i in itemslist:
        try:
            orglist.remove(i)
        except ValueError:
            pass

    return orglist

def mergelist_remove_duplicates(first_list, second_list):
    in_first = set(first_list)
    in_second = set(second_list)

    in_second_but_not_in_first = in_second - in_first
    result = first_list + list(in_second_but_not_in_first)

    return result

def find_differences_in_list(list1, list2):
    return (list(list(set(list1)-set(list2)) + list(set(list2)-set(list1))))


