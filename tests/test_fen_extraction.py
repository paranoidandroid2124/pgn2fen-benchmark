import pytest

from pgn2fen.utils import extract_fen_from_text


@pytest.mark.parametrize(
    "input, output",
    [
        pytest.param(
            "Here is a FEN to extract: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"],
            id="Starting position",
        ),
        pytest.param(
            "Here is a FEN to extract: pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            [],
            id="Less than 8 ranks invalidates FEN",
        ),
        pytest.param(
            "Here is a FEN to extract: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq 0 1",
            [],
            id="Missing en passant target square",
        ),
        pytest.param(
            "Here is a FEN to extract: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR a KQkq - 0 1",
            [],
            id="Invalid turn",
        ),
    ],
)
def test_extract_fen_from_text(input, output):
    """
    Test the extract_fen_from_text function.
    """
    result = extract_fen_from_text(input)
    assert result == output
