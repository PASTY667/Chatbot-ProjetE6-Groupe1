import unittest

from Vector.chroma_client import _sanitize_metadata_for_chroma


class TestChromaMetadataSanitize(unittest.TestCase):
    def test_flattens_doc_metadata_and_filters_scalars(self):
        meta = {
            "doc_metadata": {"filetype": "pdf", "page_count": 3, "source_path": "/tmp/a"},
            "char_start": 10,
            "char_end": 20,
            "overlap_with_prev": False,
            "ignore_list": ["not", "kept"],
            "nested": {"a": 1},
        }
        out = _sanitize_metadata_for_chroma(meta)
        self.assertEqual(out["filetype"], "pdf")
        self.assertEqual(out["page_count"], 3)
        self.assertEqual(out["char_start"], 10)
        self.assertEqual(out["char_end"], 20)
        self.assertEqual(out["overlap_with_prev"], False)
        self.assertNotIn("ignore_list", out)
        self.assertNotIn("nested", out)

    def test_handles_empty_or_none(self):
        self.assertEqual(_sanitize_metadata_for_chroma(None), {})
        self.assertEqual(_sanitize_metadata_for_chroma({}), {})


if __name__ == "__main__":
    unittest.main()
