import hypothesis
from hypothesis.strategies import binary
import json
import six
import unittest

import mini_patch


class TestFunction(object):

    def test(self):
        patch = mini_patch.make_mini_patch(self.a, self.b)
        maybe_b, success = mini_patch.apply_mini_patch(self.a, patch)
        self.assertTrue(success)
        self.assertEqual(maybe_b, self.b)
        # In Python 3, the output of SequenceMatcher.get_opcodes() doesn't seem
        # to be deterministic anymore. This is fine, because there are many
        # correct patch sequences for any given 2 inputs. However, it means
        # that we can't reliably check the output value of make_mini_patch
        # anymore.
        #self.assertEqual(patch, self.patch)


class SimpleInsert(TestFunction, unittest.TestCase):
    a = six.b('hello there')
    b = six.b('hello, how are you doing there')


class SimpleReplace(TestFunction, unittest.TestCase):
    a = six.b('i like cheetos')
    b = six.b('i hate cheetos')


class SimpleDelete(TestFunction, unittest.TestCase):
    a = six.b('i dont love lamp')
    b = six.b('i love lamp')


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

big_json_a = json.dumps(big_json).encode('utf-8')

big_json['bargle'][0]['blah'][1] = 99
big_json['bargle'][1]['bloo'] = 'barf'
del big_json['argle']
big_json_b = json.dumps(big_json).encode('utf-8')


class BigJsonTest(TestFunction, unittest.TestCase):
    a = big_json_a
    b = big_json_b


class TestPatchAndApplyBinary(unittest.TestCase):

    @hypothesis.given(binary(), binary())
    @hypothesis.settings(max_examples=1000)
    def test(self, a, b):
        patch = mini_patch.make_mini_patch(a, b)
        maybe_b, success = mini_patch.apply_mini_patch(a, patch)
        self.assertTrue(success)
        self.assertEqual(maybe_b, b)


if __name__ == '__main__':
    unittest.main()
