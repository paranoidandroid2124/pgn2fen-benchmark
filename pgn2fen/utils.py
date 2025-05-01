import re

import chess


def is_valid_fen(fen: str) -> bool:
    """
    Strict validation of FEN strings. Does not check for legality of the position.

    Args:
        fen (str): The FEN string to validate.

    Returns:
        bool: True if the FEN string is valid, False otherwise.
    """
    try:
        chess.Board(fen)
        return True
    except ValueError:
        return False


def is_fen(fen: str) -> bool:
    """
    Lenient validation of FEN strings. Checks for the basic structure of a FEN string.

    Only checks that the first component is a valid piece placement string (note: does
    not check for legality of the position) and that the last two components are
    integers. Does not validate the turn, castling rights, or en passant target square.

    Args:
        fen (str): The FEN string to validate.

    Returns:
        bool: True if the FEN string is valid, False otherwise.
    """
    components = fen.split()
    if len(components) < 3 or len(components) > 6:
        return False

    # evaluate position component against position regex
    fen_position_regex = re.compile(r"^[rnbqkpRNBQKP1-8]+(?:/[rnbqkpRNBQKP1-8]+){7}$")
    if not fen_position_regex.match(components[0]):
        return False

    # evaluate last two components as integers
    if not components[-2].isdigit() or not components[-1].isdigit():
        return False

    return True


def extract_fen_from_text(text: str) -> list[str]:
    """
    Extract FEN strings from the given text.

    Args:
        text (str): The text to search for FEN strings.

    Returns:
        list[str]: A list of extracted FEN strings.
    """
    fen_candidate_regex = re.compile(
        r"([rnbqkpRNBQKP1-8]+(?:/[rnbqkpRNBQKP1-8]+){7} [wb] (?:-|[KQkq]{1,4}) (?:-|[a-h][36]) \d+ \d+)"  # noqa: E501
    )
    return fen_candidate_regex.findall(text)


def process_llm_raw_text(llm_raw_text: str, extract_fen: bool = False) -> str | None:
    """
    Process the raw text from the LLM to extract a FEN string.

    If the raw text is a valid FEN string, it is returned as is. If not, the function
    attempts to extract a FEN string from the text using the `extract_fen_from_text`

    Args:
        llm_raw_text (str): The raw text from the LLM.
        extract_fen (bool): Whether to extract FEN strings from the text.

    Returns:
        str | None: The extracted FEN string if found, otherwise None.
    """
    if is_fen(llm_raw_text):
        return llm_raw_text
    if extract_fen:
        fen = next((fen for fen in extract_fen_from_text(llm_raw_text) if is_fen(fen)), None)
        if fen:
            return fen
    return None
