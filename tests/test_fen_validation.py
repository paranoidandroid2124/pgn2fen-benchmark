import pytest

from pgn2fen.utils import is_fen, is_valid_fen


@pytest.mark.parametrize(
    "fen_str, expected",
    [
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            True,
            id="Valid initial position",
        ),
        pytest.param(
            "rrrrrrrr/rrrrrrrr/8/8/8/8/rrrrrrrr/rrrrrrrr w KQkq - 0 1",
            True,
            id="Illegal positions don't invalidate FEN",
        ),
        pytest.param(
            "r/rrrrrrrr/8/8/8/8/rrrrrrrr/rrrrrrrr w KQkq - 0 1",
            False,
            id="Less than 8 files in a rank invalidates FEN",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            False,
            id="Less than 8 files in a rank invalidates FEN",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq 0 1",
            False,
            id="Missing en passant target square",
        ),
    ],
)
def test_is_valid_fen(fen_str, expected):
    result = is_valid_fen(fen_str)
    assert result == expected


@pytest.mark.parametrize(
    "fen_str, expected",
    [
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            True,
            id="Valid initial position",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq 0 1",
            True,
            id="Missing en passant target square",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR 0 1",
            True,
            id="Missing turn, castling rights, and en passant target square",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR - 0 1",
            True,
            id="Two missing components",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR a3 w KQkq 0 1",
            True,
            id="Incorrectly ordered turn, castling rights, and en passant target square",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR a3 1",
            False,
            id="Missing halfmove clock/fullmove number (1)",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - a3 1",
            False,
            id="Missing halfmove clock/fullmove number (2)",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR NOT_EVALUATED NOT_EVALUATED NOT_EVALUATED 0 1",
            True,
            id="Central three components are not evaluated for validity",
        ),
    ],
)
def test_is_fen(fen_str, expected):
    result = is_fen(fen_str)
    assert result == expected
