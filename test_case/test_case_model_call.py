import unittest

from model_call import model_call_batch, model_call_single


class TestModelCalls(unittest.TestCase):

    def test_model_call_batch(self):
        result = model_call_batch(["Hello", "World"])
        self.assertEqual(result.shape, (2, 500))

    def test_model_call_single(self):
        result = model_call_single("Hello")
        self.assertEqual(result.shape, (500,))


if __name__ == "__main__":
    unittest.main()
