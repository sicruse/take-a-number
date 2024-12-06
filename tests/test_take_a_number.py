import unittest
import json
import os
import tempfile
import shutil
from app import app


class TestSequenceService(unittest.TestCase):
    def setUp(self):
        """Set up test client and create a temporary directory for test files"""
        self.app = app.test_client()
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        # Set the sequence file path to our test directory
        test_file = os.path.join(self.test_dir, "test_sequences.json")
        app.config["SEQUENCE_FILE"] = test_file
        # Initialize empty sequence file
        with open(test_file, "w") as f:
            json.dump({}, f)

    def tearDown(self):
        """Clean up test files after each test"""
        shutil.rmtree(self.test_dir)

    def test_get_first_value(self):
        """Test getting the first value of a new sequence"""
        response = self.app.get("/next/test_sequence")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["sequence_id"], "test_sequence")
        self.assertEqual(data["next_value"], 1)

    def test_sequential_values(self):
        """Test getting multiple sequential values"""
        # Get first value
        response1 = self.app.get("/next/seq1")
        data1 = json.loads(response1.data)

        # Get second value
        response2 = self.app.get("/next/seq1")
        data2 = json.loads(response2.data)

        # Get third value
        response3 = self.app.get("/next/seq1")
        data3 = json.loads(response3.data)

        self.assertEqual(data1["next_value"], 1)
        self.assertEqual(data2["next_value"], 2)
        self.assertEqual(data3["next_value"], 3)

    def test_multiple_sequences(self):
        """Test maintaining multiple independent sequences"""
        # Get values for sequence A
        response_a1 = self.app.get("/next/seq_a")
        response_a2 = self.app.get("/next/seq_a")

        # Get values for sequence B
        response_b1 = self.app.get("/next/seq_b")

        data_a1 = json.loads(response_a1.data)
        data_a2 = json.loads(response_a2.data)
        data_b1 = json.loads(response_b1.data)

        self.assertEqual(data_a1["next_value"], 1)
        self.assertEqual(data_a2["next_value"], 2)
        self.assertEqual(data_b1["next_value"], 1)

    def test_persistence(self):
        """Test that values persist between requests"""
        # Get initial value
        self.app.get("/next/persist_test")

        # Verify file exists and contains correct data
        with open(app.config["SEQUENCE_FILE"], "r") as f:
            data = json.load(f)
            self.assertEqual(data["persist_test"], 1)

        # Get next value
        response = self.app.get("/next/persist_test")
        data = json.loads(response.data)
        self.assertEqual(data["next_value"], 2)

    def test_invalid_sequence_id(self):
        """Test handling of invalid sequence IDs"""
        # Test empty sequence ID
        response = self.app.get("/next/")
        self.assertEqual(response.status_code, 404)

        # Test with special characters (if implemented)
        response = self.app.get("/next/test@sequence")
        # Should handle special chars
        self.assertEqual(response.status_code, 200)

    def test_concurrent_access(self):
        """Test handling of concurrent access to the same sequence"""
        from concurrent.futures import ThreadPoolExecutor
        import threading

        def get_next():
            return self.app.get("/next/concurrent_test")

        # Create multiple threads to access the same sequence
        with ThreadPoolExecutor(max_workers=10) as executor:
            responses = list(executor.map(lambda _: get_next(), range(10)))

        # Convert responses to values
        values = [json.loads(r.data)["next_value"] for r in responses]

        # Check that we got all unique values from 1 to 10
        self.assertEqual(sorted(values), list(range(1, 11)))

    def test_file_corruption_recovery(self):
        """Test recovery from corrupted sequence file"""
        # Write invalid JSON to sequence file
        with open(app.config["SEQUENCE_FILE"], "w") as f:
            f.write("invalid json{")

        # Service should handle corrupted file gracefully
        response = self.app.get("/next/new_sequence")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["next_value"], 1)

    def test_large_numbers(self):
        """Test handling of large sequence numbers"""
        # Manually set a large initial value
        with open(app.config["SEQUENCE_FILE"], "w") as f:
            json.dump({"large_seq": 999999999}, f)

        # Get next value
        response = self.app.get("/next/large_seq")
        data = json.loads(response.data)

        self.assertEqual(data["next_value"], 1000000000)


if __name__ == "__main__":
    unittest.main()
