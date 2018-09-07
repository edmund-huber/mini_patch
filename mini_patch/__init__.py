import difflib
import json
import string


VERSION = 0


def make_mini_patch(a, b):
    s_m = difflib.SequenceMatcher(None, a, b)
    mini_patch = '{}!'.format(VERSION)
    for tag, i1, i2, j1, j2 in s_m.get_opcodes():
        if tag == 'replace':
            _len1 = i2 - i1
            _len2 = j2 - j1
            mini_patch += 'r:{},{},${}${};'.format(i1, _len1, _len2, b[j1:j2])
        elif tag == 'delete':
            _len = i2 - i1
            mini_patch += 'd:{},{};'.format(i1, _len)
        elif tag == 'insert':
            assert i1 == i2
            _len = j2 - j1
            mini_patch += 'i:{},${}${};'.format(i1, _len, b[j1:j2])
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
    b = str(a)
    b_indices = range(len(a))
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
                if version != 0:
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
                where = b_indices.index(where)
                b = b[:where] + what + b[where+how_much:]
                b_indices = b_indices[:where] + ([None] * len(what)) + b_indices[where+how_much:]
                op = None
                params = []
            elif op == 'd' and len(params) == 2:
                # Apply 'delete' op.
                where, how_much = params
                where = b_indices.index(where)
                b = b[:where] + b[where+how_much:]
                b_indices = b_indices[:where] + b_indices[where+how_much:]
                op = None
                params = []
            elif op == 'i' and len(params) == 2:
                # Apply 'insert' op.
                where, what = params
                if where < len(a):
                    where = b_indices.index(where)
                    b = b[:where] + what + b[where:]
                    b_indices = b_indices[:where] + ([None] * len(what)) + b_indices[where:]
                else:
                    # Insert may wish to put things at the end, which we don't
                    # have an index for.
                    b = b + what
                    b_indices = b_indices + ([None] * len(what))
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
        return b, False
    return b, True
