from app.rag.splitter import split_text


def test_split_text():
    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = split_text(
        text,
        chunk_size=10,
        chunk_overlap=2
    )

    assert len(chunks) > 1
    assert "".join(chunks) != ""
    assert chunks[0] == "abcdefghij"