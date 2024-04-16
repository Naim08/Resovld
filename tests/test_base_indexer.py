# import os
# import unittest
# from unittest.mock import patch, MagicMock
# from indexers.base_indexer import BaseIndexer  # Ensure your class is importable

# class TestBaseIndexer(unittest.TestCase):

#     @patch("os.makedirs")
#     @patch("os.path.exists", return_value=False)
#     def test_save_to_disk_path_not_exists(self, mock_exists, mock_makedirs):
#         path = "/path/to/repo"
#         BaseIndexer.save_to_disk(path)

#         # Ensure makedirs was called since the path does not exist
#         mock_makedirs.assert_called_once_with(path)

#     @patch("os.path.exists", return_value=True)
#     @patch("os.listdir", return_value=["dummy_item"])
#     @patch("os.walk", return_value=[("root", ["dir"], ["file"])])
#     @patch("os.remove")
#     @patch("os.rmdir")
#     def test_save_to_disk_non_empty_path(
#         self, mock_rmdir, mock_remove, mock_walk, mock_listdir, mock_exists
#     ):
#         path = "/path/to/repo"
#         BaseIndexer.save_to_disk(path)

#         # Ensure os.remove and os.rmdir were called since the directory is not empty
#         mock_remove.assert_called_once_with(os.path.join("root", "file"))
#         mock_rmdir.assert_called_once_with(os.path.join("root", "dir"))

#     @patch("os.makedirs")
#     @patch("os.path.exists", side_effect=OSError("Mock OS Error"))
#     def test_save_to_disk_os_error_path_exists(self, mock_exists, mock_makedirs):
#         path = "/path/to/repo"

#         with self.assertRaises(OSError):
#             BaseIndexer.save_to_disk(path)

#         mock_makedirs.assert_not_called()

#     @patch("os.path.exists", return_value=True)
#     @patch("os.listdir", return_value=["dummy_item"])
#     @patch("os.walk", return_value=[("root", ["dir"], ["file"])])
#     @patch("os.remove", side_effect=OSError("Mock OS Error"))
#     @patch("os.rmdir")
#     def test_save_to_disk_os_error_file_removal(
#             self, mock_rmdir, mock_remove, mock_walk, mock_listdir, mock_exists
#     ):
#         path = "/path/to/repo"

#         with self.assertRaises(OSError):
#             BaseIndexer.save_to_disk(path)

#         # Ensure os.remove was called before the error was raised
#         mock_remove.assert_called_once_with(os.path.join("root", "file"))
#         mock_rmdir.assert_not_called()


# if __name__ == "__main__":
#     unittest.main()
