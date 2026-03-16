
import unittest
import tempfile
import shutil
import os
import json
from pathlib import Path
from scripts.daily_ai.processors.deduplicator import Deduplicator
from scripts.daily_ai.models import BaseItem

class TestDeduplicatorPersistence(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.history_file = Path(self.test_dir) / "history.json"
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def test_persistence(self):
        # 1. Run first time
        dedup1 = Deduplicator(history_file=self.history_file)
        items1 = [
            BaseItem(title="Item 1", url="http://example.com/1", source="test"),
            BaseItem(title="Item 2", url="http://example.com/2", source="test")
        ]
        unique1 = dedup1.process(items1)
        self.assertEqual(len(unique1), 2)
        dedup1.save_state()
        
        # Verify file exists
        self.assertTrue(self.history_file.exists())
        
        # 2. Run second time with overlap
        dedup2 = Deduplicator(history_file=self.history_file)
        items2 = [
            BaseItem(title="Item 2", url="http://example.com/2", source="test"), # Duplicate
            BaseItem(title="Item 3", url="http://example.com/3", source="test")  # New
        ]
        unique2 = dedup2.process(items2)
        
        # Should only have Item 3
        self.assertEqual(len(unique2), 1)
        self.assertEqual(unique2[0].title, "Item 3")
        
    def test_title_similarity(self):
        dedup = Deduplicator(history_file=self.history_file)
        items = [
            BaseItem(title="My Great Project", url="http://example.com/1", source="test"),
        ]
        dedup.process(items)
        dedup.save_state()
        
        dedup2 = Deduplicator(history_file=self.history_file)
        items2 = [
            BaseItem(title="my great project", url="http://example.com/2", source="test") # Similar title
        ]
        unique2 = dedup2.process(items2)
        self.assertEqual(len(unique2), 0)

if __name__ == '__main__':
    unittest.main()
