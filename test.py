import hypothesis
from hypothesis.strategies import binary
import json
import unittest

import mini_patch


class TestFormAndFunction(object):

    def test(self):
        patch = mini_patch.make_mini_patch(self.a, self.b)
        assert patch == self.patch, patch
        maybe_b, success = mini_patch.apply_mini_patch(self.a, patch)
        assert success
        assert maybe_b == self.b, maybe_b


class SimpleInsert(TestFormAndFunction, unittest.TestCase):
    a = 'hello there'
    b = 'hello, how are you doing there'
    patch = '0!i:5,$19$, how are you doing;'


class SimpleReplace(TestFormAndFunction, unittest.TestCase):
    a = 'i like cheetos'
    b = 'i hate cheetos'
    patch = '0!r:2,3,$3$hat;'


class SimpleDelete(TestFormAndFunction, unittest.TestCase):
    a = 'i dont love lamp'
    b = 'i love lamp'
    patch = '0!d:1,5;'


big_json = {
    'argle': 5,
    'bargle': [
        {
            'bloo': 5,
            'blah': [1, 2, 3]
        },
        {
            'bloo': 33,
            'blah': [3, 4, 5]
        }
    ]
}

big_json_a = json.dumps(big_json)

big_json['bargle'][0]['blah'][1] = 99
big_json['bargle'][1]['bloo'] = 'barf'
del big_json['argle']
big_json_b = json.dumps(big_json)


class BigJsonTest(TestFormAndFunction, unittest.TestCase):
    a = big_json_a
    b = big_json_b
    patch = '0!d:1,12;r:48,1,$2$99;r:65,2,$6$"barf";'


class TestPatchAndApplyBinary(unittest.TestCase):

    @hypothesis.given(binary(), binary())
    @hypothesis.settings(max_examples=1000)
    def test(self, a, b):
        patch = mini_patch.make_mini_patch(a, b)
        maybe_b, success = mini_patch.apply_mini_patch(a, patch)
        assert success
        assert maybe_b == b


if __name__ == '__main__':
    unittest.main()
