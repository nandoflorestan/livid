import unittest
import random
from yid import encode_yid, decode_yid, random_yid_int, random_yid_str


class TestYidStaticVectors(unittest.TestCase):
    def test_known_small(self):
        # Integer 0 should encode to all 'A's (index 0)
        self.assertEqual(encode_yid(0, 1), "A")
        self.assertEqual(encode_yid(0, 5), "AAAAA")
        self.assertEqual(encode_yid(0, 11), "AAAAAAAAAAA")
        self.assertEqual(decode_yid("A"), 0)
        self.assertEqual(decode_yid("AAAAA"), 0)
        self.assertEqual(decode_yid("AAAAAAAAAAA"), 0)
        # Integer 1
        self.assertEqual(encode_yid(1, 1), "B")
        self.assertEqual(encode_yid(1, 5), "AAAAB")
        self.assertEqual(encode_yid(1, 11), "AAAAAAAAAAB")
        self.assertEqual(decode_yid("B"), 1)
        self.assertEqual(decode_yid("AAAAB"), 1)
        self.assertEqual(decode_yid("AAAAAAAAAAB"), 1)
        # Integer 64
        self.assertEqual(encode_yid(64, 5), "AAABA")
        self.assertEqual(encode_yid(64, 11), "AAAAAAAAABA")
        self.assertEqual(decode_yid("AAABA"), 64)
        self.assertEqual(decode_yid("AAAAAAAAABA"), 64)

    def test_known_bits(self):
        # max values
        self.assertEqual(encode_yid((1 << 6) - 1, 1), "_")  # index 63
        self.assertEqual(decode_yid("_"), 63)
        # 11-char max (2^64-1)
        max64 = (1 << 64) - 1
        s = encode_yid(max64, 11)
        self.assertEqual(len(s), 11)
        self.assertEqual(decode_yid(s), max64)


class TestYidRandomRoundtrip(unittest.TestCase):
    def test_random_int_encode_decode(self):
        for length in range(1, 12):
            for _ in range(1000):
                n = random_yid_int(length)
                s = encode_yid(n, length)
                self.assertEqual(decode_yid(s), n)

    def test_random_str_decode_encode(self):
        # from random string, decode then re-encode round-trip
        for length in [1, 5, 11]:
            for _ in range(500):
                s = random_yid_str(length)
                n = decode_yid(s)
                s2 = encode_yid(n, length)
                self.assertEqual(s2, s)


class TestYidErrorCases(unittest.TestCase):
    def test_encode_value_too_large(self):
        with self.assertRaises(ValueError):
            encode_yid(1 << 6, 1)
        with self.assertRaises(ValueError):
            encode_yid(1 << 65, 11)

    def test_decode_invalid_length(self):
        with self.assertRaises(ValueError):
            decode_yid("")
        with self.assertRaises(ValueError):
            decode_yid("A" * 12)

    def test_decode_invalid_chars(self):
        with self.assertRaises(ValueError):
            decode_yid("*")
        with self.assertRaises(ValueError):
            decode_yid("?????")

    def test_decode_11char_overflows(self):
        # Craft a string that decodes to >=2^64
        invalid = encode_yid((1 << 64) - 1, 11)
        # Manually increase top bits by substituting first char with high bits
        # B64_INDEX['-'] = 62 so upper bits nonzero
        bad = "-" + invalid[1:]
        with self.assertRaises(ValueError):
            decode_yid(bad)


# Run tests via `python -m unittest discover`
if __name__ == "__main__":
    unittest.main()
