import pytest

from chunked_upload import ChunkedUpload


def test_receive_and_missing():
    up = ChunkedUpload(total_chunks=3)
    assert up.missing() == [0, 1, 2]
    assert up.receive(1, b"B") == "stored"
    assert up.missing() == [0, 2]
    assert up.is_complete() is False


def test_duplicate_chunk_is_harmless():
    up = ChunkedUpload(total_chunks=3)
    assert up.receive(0, b"A") == "stored"
    # A flaky connection re-sends chunk 0:
    assert up.receive(0, b"A") == "duplicate"
    assert up.missing() == [1, 2]


def test_out_of_range_chunk_raises():
    up = ChunkedUpload(total_chunks=2)
    with pytest.raises(IndexError):
        up.receive(2, b"X")
    with pytest.raises(IndexError):
        up.receive(-1, b"X")


def test_complete_and_assemble_out_of_order():
    up = ChunkedUpload(total_chunks=3)
    up.receive(2, b"C")   # arrives out of order
    up.receive(0, b"A")
    assert up.is_complete() is False
    up.receive(1, b"B")
    assert up.is_complete() is True
    assert up.assemble() == [b"A", b"B", b"C"]  # reassembled in index order


def test_assemble_incomplete_raises():
    up = ChunkedUpload(total_chunks=2)
    up.receive(0, b"A")
    with pytest.raises(ValueError):
        up.assemble()
