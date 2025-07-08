import unittest
import random
from livid import encode_livid, decode_livid, random_livid_int, random_livid_str


class TestYidStaticVectors(unittest.TestCase):
    def test_known_small(self):
        # Integer 0 should encode to all 'A's (index 0)
        self.assertEqual(encode_livid(0, 1), "A")
        self.assertEqual(encode_livid(0, 5), "AAAAA")
        self.assertEqual(encode_livid(0, 11), "AAAAAAAAAAA")
        self.assertEqual(decode_livid("A"), 0)
        self.assertEqual(decode_livid("AAAAA"), 0)
        self.assertEqual(decode_livid("AAAAAAAAAAA"), 0)
        # Integer 1
        self.assertEqual(encode_livid(1, 1), "B")
        self.assertEqual(encode_livid(1, 5), "AAAAB")
        self.assertEqual(encode_livid(1, 11), "AAAAAAAAAAB")
        self.assertEqual(decode_livid("B"), 1)
        self.assertEqual(decode_livid("AAAAB"), 1)
        self.assertEqual(decode_livid("AAAAAAAAAAB"), 1)
        # Integer 64
        self.assertEqual(encode_livid(64, 5), "AAABA")
        self.assertEqual(encode_livid(64, 11), "AAAAAAAAABA")
        self.assertEqual(decode_livid("AAABA"), 64)
        self.assertEqual(decode_livid("AAAAAAAAABA"), 64)

    def test_known_bits(self):
        # max values
        self.assertEqual(encode_livid((1 << 6) - 1, 1), "_")  # index 63
        self.assertEqual(decode_livid("_"), 63)
        # 11-char max (2^64-1)
        max64 = (1 << 64) - 1
        s = encode_livid(max64, 11)
        self.assertEqual(len(s), 11)
        self.assertEqual(decode_livid(s), max64)


class TestYidRandomRoundtrip(unittest.TestCase):
    def test_random_int_encode_decode(self):
        for length in range(1, 12):
            for _ in range(1000):
                n = random_livid_int(length)
                s = encode_livid(n, length)
                self.assertEqual(decode_livid(s), n)

    def test_random_str_decode_encode(self):
        # from random string, decode then re-encode round-trip
        for length in [1, 5, 11]:
            for _ in range(500):
                s = random_livid_str(length)
                n = decode_livid(s)
                s2 = encode_livid(n, length)
                self.assertEqual(s2, s)


class TestYidErrorCases(unittest.TestCase):
    def test_encode_value_too_large(self):
        with self.assertRaises(ValueError):
            encode_livid(1 << 6, 1)
        with self.assertRaises(ValueError):
            encode_livid(1 << 65, 11)

    def test_decode_invalid_length(self):
        with self.assertRaises(ValueError):
            decode_livid("")
        with self.assertRaises(ValueError):
            decode_livid("A" * 12)

    def test_decode_invalid_chars(self):
        with self.assertRaises(ValueError):
            decode_livid("*")
        with self.assertRaises(ValueError):
            decode_livid("?????")

    def test_decode_11char_overflows(self):
        # Craft a string that decodes to >=2^64
        invalid = encode_livid((1 << 64) - 1, 11)
        # Manually increase top bits by substituting first char with high bits
        # B64_INDEX['-'] = 62 so upper bits nonzero
        bad = "-" + invalid[1:]
        with self.assertRaises(ValueError):
            decode_livid(bad)


# Run tests via `python -m unittest discover`
if __name__ == "__main__":
    unittest.main()
