import base64
import difflib
import json
import six
import string


VERSION = 1


def make_mini_patch(a, b):
    if not isinstance(a, six.binary_type):
        raise TypeError("a bytes-like object is required, not '{}'".format(type(a).__name__))
    if not isinstance(b, six.binary_type):
        raise TypeError("a bytes-like object is required, not '{}'".format(type(b).__name__))

    s_m = difflib.SequenceMatcher(isjunk=None, a=a, b=b, autojunk=False)
    mini_patch = '{}!'.format(VERSION)
    first = True
    for tag, i1, i2, j1, j2 in s_m.get_opcodes():
        if first:
            assert i1 == j1 == 0
            first = False
        else:
            assert i1 == prev_i2
            assert j1 == prev_j2
        prev_i2 = i2
        prev_j2 = j2
        if tag == 'replace':
            b64_encoded = base64.b64encode(b[j1:j2]).decode('ascii')
            mini_patch += 'r:{},{},${}${};'.format(i1, i2 - i1, len(b64_encoded), b64_encoded)
        elif tag == 'delete':
            mini_patch += 'd:{},{};'.format(i1, i2 - i1)
        elif tag == 'insert':
            assert i1 == i2
            b64_encoded = base64.b64encode(b[j1:j2]).decode('ascii')
            mini_patch += 'i:{},${}${};'.format(i1, len(b64_encoded), b64_encoded)
        elif tag == 'equal':
            pass
    return mini_patch


class BadMiniPatch(Exception):
    pass


def _read_mini_int(s, i, terminators):
    integer = 0
    while s[i] not in terminators:
        integer = (integer * 10) + int(s[i])
        i += 1
    return i, integer


def apply_mini_patch(a, mini_patch):
    orig_len = len(a)
    a_indices = list(range(len(a)))
    version = None
    op = None
    params = []
    eat = None
    i = 0
    try:
        old_i_op = None
        while i < len(mini_patch) or op is not None:
            if (i, op) == old_i_op:
                raise BadMiniPatch('no progress')
            old_i_op = (i, op)
            if version is None:
                i, version = _read_mini_int(mini_patch, i, '!')
                i += 1
                if version != VERSION:
                    raise BadMiniPatch()
            elif eat is not None:
                if mini_patch[i] not in eat:
                    raise BadMiniPatch()
                i += 1
                eat = None
            elif op is None:
                op = mini_patch[i]
                if mini_patch[i + 1] != ':':
                    raise BadMiniPatch()
                i += 2
            elif op == 'r' and len(params) == 3:
                # Apply 'replace' op.
                where, how_much, what = params
                what = base64.b64decode(what)
                where = a_indices.index(where)
                a = a[:where] + what + a[where+how_much:]
                a_indices = a_indices[:where] + ([None] * len(what)) + a_indices[where+how_much:]
                op = None
                params = []
            elif op == 'd' and len(params) == 2:
                # Apply 'delete' op.
                where, how_much = params
                where = a_indices.index(where)
                a = a[:where] + a[where+how_much:]
                a_indices = a_indices[:where] + a_indices[where+how_much:]
                op = None
                params = []
            elif op == 'i' and len(params) == 2:
                # Apply 'insert' op.
                where, what = params
                what = base64.b64decode(what)
                if where < orig_len:
                    where = a_indices.index(where)
                    a = a[:where] + what + a[where:]
                    a_indices = a_indices[:where] + ([None] * len(what)) + a_indices[where:]
                else:
                    # Insert may wish to put things at the end, which we don't
                    # have an index for.
                    a = a + what
                    a_indices = a_indices + ([None] * len(what))
                op = None
                params = []
            else:
                # Expecting another parameter, which is either an integer:
                if mini_patch[i] in map(str, range(0, 10)):
                    i, integer = _read_mini_int(mini_patch, i, ',;')
                    params.append(integer)
                    eat = ',;'
                elif mini_patch[i] == '$':
                    # Or a pascal string.
                    i += 1
                    i, _len = _read_mini_int(mini_patch, i, '$')
                    i += 1
                    s = mini_patch[i:i+_len]
                    i += _len
                    params.append(s)
                    eat = ',;'
                else:
                    raise BadMiniPatch()
    except (KeyError, BadMiniPatch):
        return a, False
    return a, True
