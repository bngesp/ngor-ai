import unittest
from app.utils.diff_processor import DiffProcessor
from app.models.config import CodeReviewConfig
from app.models.gitlab import Change

class TestDiffProcessor(unittest.TestCase):
    def setUp(self):
        # Create a test configuration
        self.config = CodeReviewConfig(
            file_extensions=[".py", ".js"],
            excluded_paths=["vendor/", "node_modules/"],
            max_files_per_review=5,
            max_lines_per_file=100
        )
        
        self.diff_processor = DiffProcessor(self.config)
    
    def test_should_review_file(self):
        # Test files that should be reviewed
        self.assertTrue(self.diff_processor.should_review_file("app/main.py"))
        self.assertTrue(self.diff_processor.should_review_file("src/components/Button.js"))
        
        # Test files that should be excluded based on extension
        self.assertFalse(self.diff_processor.should_review_file("README.md"))
        self.assertFalse(self.diff_processor.should_review_file("docs/architecture.txt"))
        
        # Test files that should be excluded based on path
        self.assertFalse(self.diff_processor.should_review_file("vendor/package/lib.py"))
        self.assertFalse(self.diff_processor.should_review_file("node_modules/react/index.js"))
    
    def test_count_diff_lines(self):
        # Simple diff with 3 content lines
        simple_diff = """
--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
-old line
+new line
 unchanged line
+another new line
"""
        self.assertEqual(self.diff_processor._count_diff_lines(simple_diff), 3)
        
        # Empty diff
        self.assertEqual(self.diff_processor._count_diff_lines(""), 0)
    
    def test_filter_changes(self):
        # Create test changes
        changes = [
            Change(
                old_path="app/main.py",
                new_path="app/main.py",
                diff="@@ -1,1 +1,1 @@\n-old\n+new",
                deleted_file=False
            ),
            Change(
                old_path="README.md",
                new_path="README.md",
                diff="@@ -1,1 +1,1 @@\n-old\n+new",
                deleted_file=False
            ),
            Change(
                old_path="app/deleted.py",
                new_path="app/deleted.py",
                diff="",
                deleted_file=True
            ),
            Change(
                old_path="vendor/lib.py",
                new_path="vendor/lib.py",
                diff="@@ -1,1 +1,1 @@\n-old\n+new",
                deleted_file=False
            ),
            # Create a large diff that exceeds the max lines
            Change(
                old_path="app/large.py",
                new_path="app/large.py",
                diff="@@ -1,200 +1,200 @@\n" + "-old\n+new\n" * 101,  # More than max_lines_per_file
                deleted_file=False
            )
        ]
        
        filtered = self.diff_processor.filter_changes(changes)
        
        # We should only have the first change (app/main.py)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].new_path, "app/main.py")
        
    def test_extract_diff_chunks(self):
        # Test with a diff that has multiple chunks
        multi_chunk_diff = """
@@ -1,3 +1,4 @@
 line1
-old line2
+new line2
+new line2.5
 line3
@@ -10,2 +11,3 @@
 line10
+new line10.5
 line11
"""
        chunks = self.diff_processor.extract_diff_chunks(multi_chunk_diff)
        
        # We should have 2 chunks
        self.assertEqual(len(chunks), 2)
        
        # First chunk should start at line 1
        self.assertEqual(chunks[0]['new_start'], 1)
        
        # Second chunk should start at line 11
        self.assertEqual(chunks[1]['new_start'], 11)
        
    def test_chunk_large_diff(self):
        # Create a large diff
        large_diff = "line\n" * 1000
        chunks = self.diff_processor.chunk_large_diff(large_diff, max_lines=200)
        
        # We should have 5 chunks (1000 / 200 = 5)
        self.assertEqual(len(chunks), 5)

if __name__ == '__main__':
    unittest.main()