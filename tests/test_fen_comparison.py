import pytest

from pgn2fen.evaluate import (
    compare_en_passant,
    compare_fens,
    is_en_passant,
    prepare_llm_fen,
    prepare_true_fen,
)


def test_prepare_true_fen_valid():
    fen_str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    fen = prepare_true_fen(fen_str)
    assert fen.piece_placement == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    assert fen.turn == "w"
    assert fen.castling == "KQkq"
    assert fen.en_passant == "-"
    assert fen.halfmove_clock == 0
    assert fen.fullmove_number == 1


def test_prepare_true_fen_invalid():
    with pytest.raises(ValueError):
        prepare_true_fen("Invalid true fen string")


@pytest.mark.parametrize(
    "llm_fen_str, piece_placement, turn, castling, en_passant, halfmove_clock, fullmove_number",
    [
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            "w",
            "KQkq",
            "-",
            0,
            1,
            id="Starting position",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            None,
            None,
            None,
            0,
            1,
            id="Missing turn, castling rights, and en passant",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            "w",
            "KQkq",
            None,
            0,
            1,
            id="Missing en passant target square",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            "w",
            "-",
            None,
            0,
            1,
            id="Missing en passant target square. '-' defaults to castling rights.",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR - 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            None,
            "-",
            None,
            0,
            1,
            id="Missing turn and castling rights. '-' defaults to castling rights.",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR - a3 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            None,
            "-",
            "a3",
            0,
            1,
            id="Missing turn. '-' defaults to castling rights.",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR a3 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            None,
            None,
            "a3",
            0,
            1,
            id="Missing turn and castling rights. Square assigned to en passant.",
        ),
    ],
)
def test_prepare_llm_fen(
    llm_fen_str, piece_placement, turn, castling, en_passant, halfmove_clock, fullmove_number
):
    fen = prepare_llm_fen(llm_fen_str)
    assert fen.piece_placement == piece_placement
    assert fen.turn == turn
    assert fen.castling == castling
    assert fen.en_passant == en_passant
    assert fen.halfmove_clock == halfmove_clock
    assert fen.fullmove_number == fullmove_number


@pytest.mark.parametrize(
    "invalid_llm_fen_str",
    [
        pytest.param("invalid fen string"),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0", id="Missing fullmove number"
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 2", id="Additional number"
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq 0 1 a3", id="Additional move field"
        ),
    ],
)
def test_prepare_llm_fen_invalid(invalid_llm_fen_str):
    with pytest.raises(ValueError):
        prepare_llm_fen(invalid_llm_fen_str)


@pytest.mark.parametrize(
    "true_fen_str, llm_fen_str, expected",
    [
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            True,
            id="Identical starting board FENs",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq a3 0 1",
            True,
            id="Equivalent en passants",
        ),
        pytest.param(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq a3 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            False,
            id="Inequivalent en passants",
        ),
    ],
)
def test_compare_fens_all_match(true_fen_str, llm_fen_str, expected):
    true_fen = prepare_true_fen(true_fen_str)
    llm_fen = prepare_llm_fen(llm_fen_str)
    evaluation = compare_fens(true_fen, llm_fen)
    assert evaluation.full_correctness == expected


@pytest.mark.parametrize(
    "true_en_passant, llm_en_passant, expected",
    [
        pytest.param("e3", "e3", True),
        pytest.param("e3", "e4", False),
        pytest.param(
            "e3",
            "-",
            False,
            id="If true en passant specifies a square, the LLM en passant must reflect it",
        ),
        pytest.param(
            "-",
            "e3",
            True,
            id="If true en passant is '-', the LLM en passant is permitted to be any valid square",
        ),
        pytest.param("-", "-", True),
        pytest.param("-", "invalid", False),
        pytest.param("-", None, False),
    ],
)
def test_compare_en_passant_valid_match(true_en_passant, llm_en_passant, expected):
    assert compare_en_passant(true_en_passant, llm_en_passant) == expected


def test_compare_en_passant_invalid_format():
    with pytest.raises(ValueError):
        compare_en_passant("invalid", "-")


@pytest.mark.parametrize(
    "en_passant_str, expected",
    [
        ("e3", True),
        ("h6", True),
        ("-", True),
        ("e2", False),
        ("h7", False),
        ("j3", False),
        ("invalid", False),
        ("--", False),
    ],
)
def test_is_en_passant(en_passant_str, expected):
    result = is_en_passant(en_passant_str)
    assert result == expected
