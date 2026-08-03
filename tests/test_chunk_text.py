from app.services.document_processor import chunk_text

# numbered words so we can tell chunks apart when something breaks
TEXT = " ".join(str(i) for i in range(1200))


def test_chunk_length():
    lengths = [len(c.split()) for c in chunk_text(TEXT, size=512, overlap=50)]

    assert lengths == [512, 512, 276]


def test_overlap_works():
    chunks = chunk_text(TEXT, size=512, overlap=50)

    for current, following in zip(chunks, chunks[1:], strict=False):
        assert current.split()[-50:] == following.split()[:50]


def test_no_empty_chunks():
    for text in ["", "   \n\t  ", "one", "two words", TEXT]:
        assert all(c.strip() for c in chunk_text(text))


def test_nothing_lost():
    chunks = chunk_text(TEXT, size=512, overlap=50)

    words = chunks[0].split()
    for chunk in chunks[1:]:
        words += chunk.split()[50:]  # skip the overlap, it is already there
    assert words == TEXT.split()
