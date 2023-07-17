import io
import pytest
import tempfile
import pathlib
from perry.documents import *


def test_save_bytes_to_file_should_create_file():
    """ Saving bytes to a file should create a file. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        bytes_obj = io.BytesIO(b"hello world")
        save_bytes_to_file(bytes_obj, tmp_dir / "test.txt")
        assert (tmp_dir / "test.txt").exists()


def test_load_bytes_from_file_should_equal_save():
    """ Loading bytes from a file should equal the original bytes. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        bytes_obj = io.BytesIO(b"hello world")
        save_bytes_to_file(bytes_obj, tmp_dir / "test.txt")
        loaded_bytes_obj = load_bytes_from_file(tmp_dir / "test.txt")
        assert bytes_obj.getbuffer() == loaded_bytes_obj.getbuffer()


def test_metadata_postfix_should_equal_meta_json():
    """ The metadata postfix should equal '_meta.json'. """
    assert metadata_postfix() == "_meta.json"


def test_metadata_filepath_should_equal_document_path_with_postfix():
    """ The document metadata filepath should equal the document path with postfix. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        metadata = DocumentMetadata(
            title="Test Title",
            summary="Test Summary",
            file_path=pathlib.Path(tmp_dir / "test.txt"),
        )
        assert get_metadata_filepath(metadata.file_path) == pathlib.Path(
            tmp_dir / "test_meta.json"
        )


def test_save_document_metadata_should_create_file():
    """ Saving document metadata should create a file. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        metadata = DocumentMetadata(
            title="Test Title",
            summary="Test Summary",
            file_path=pathlib.Path(tmp_dir / "test.txt"),
        )
        save_document_metadata(metadata)
        assert (tmp_dir / "test_meta.json").exists()


def test_load_document_metadata_should_equal_save():
    """ Loading document metadata should equal the original metadata. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        metadata = DocumentMetadata(
            title="Test Title",
            summary="Test Summary",
            file_path=pathlib.Path(tmp_dir / "test.txt"),
        )
        save_document_metadata(metadata)
        loaded_metadata = load_document_metadata(tmp_dir / "test_meta.json")
        assert metadata == loaded_metadata


def test_load_from_document_path_should_equal_save():
    """ Loading document metadata from document path should equal the original metadata. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        metadata = DocumentMetadata(
            title="Test Title",
            summary="Test Summary",
            file_path=pathlib.Path(tmp_dir / "test.txt"),
        )
        save_document_metadata(metadata)
        loaded_metadata = load_metadata_from_document_path(tmp_dir / "test.txt")
        assert metadata == loaded_metadata


def test_save_document_should_create_document_and_metadata_file():
    """ Saving document should create a file. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        metadata = DocumentMetadata(
            title="Test Title",
            summary="Test Summary",
            file_path=pathlib.Path(tmp_dir / "test.txt"),
        )
        document = io.BytesIO(b"hello world")
        save_document(document, metadata)
        assert (tmp_dir / "test.txt").exists()
        assert (tmp_dir / "test_meta.json").exists()


def test_load_document_should_equal_save():
  """ Loading documents should equal the original document and metadata. """
  with tempfile.TemporaryDirectory() as tmp_dir:
      tmp_dir = pathlib.Path(tmp_dir)
      metadata = DocumentMetadata(
          title="Test Title",
          summary="Test Summary",
          file_path=pathlib.Path(tmp_dir / "test.txt"),
      )
      document = io.BytesIO(b"hello world")
      save_document(document, metadata)
      loaded_document, metadata = load_document(tmp_dir / "test.txt")
      assert document.getbuffer() == loaded_document.getbuffer()
      assert metadata == load_document_metadata(tmp_dir / "test_meta.json")
