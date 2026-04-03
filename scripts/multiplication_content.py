from __future__ import annotations

from scripts.multiplication_common import MultiplicationFact


ANIMALS = ["ranas", "pinguinos", "zorros", "jirafas", "abejas", "gatitos"]

_NUMBER_WORDS = {
    0: "cero",
    1: "uno",
    2: "dos",
    3: "tres",
    4: "cuatro",
    5: "cinco",
    6: "seis",
    7: "siete",
    8: "ocho",
    9: "nueve",
    10: "diez",
    11: "once",
    12: "doce",
    13: "trece",
    14: "catorce",
    15: "quince",
    16: "dieciseis",
    17: "diecisiete",
    18: "dieciocho",
    19: "diecinueve",
    20: "veinte",
    21: "veintiuno",
    22: "veintidos",
    23: "veintitres",
    24: "veinticuatro",
    25: "veinticinco",
    26: "veintiseis",
    27: "veintisiete",
    28: "veintiocho",
    29: "veintinueve",
}

_TENS_WORDS = {
    30: "treinta",
    40: "cuarenta",
    50: "cincuenta",
    60: "sesenta",
    70: "setenta",
    80: "ochenta",
    90: "noventa",
    100: "cien",
}


def spanish_number(value: int) -> str:
    if value in _NUMBER_WORDS:
        return _NUMBER_WORDS[value]
    if value in _TENS_WORDS:
        return _TENS_WORDS[value]
    if 30 < value < 100:
        tens = (value // 10) * 10
        ones = value % 10
        return f"{_TENS_WORDS[tens]} y {_NUMBER_WORDS[ones]}"
    raise ValueError(f"Unsupported number: {value}")


def prompt_audio_text(fact: MultiplicationFact) -> str:
    return f"{spanish_number(fact.left)} por {spanish_number(fact.right)}"


def answer_audio_text(fact: MultiplicationFact) -> str:
    return spanish_number(fact.answer)


def animal_name(fact: MultiplicationFact) -> str:
    return ANIMALS[(fact.left + fact.right) % len(ANIMALS)]


def playful_prompt_text(fact: MultiplicationFact) -> str:
    prompts = [
        f"Da {fact.answer} palmadas",
        f"Haz {fact.left} filas de {fact.right} con monedas",
        "Dilo como un leon",
        "Cuenta primero los grupos, luego el total",
    ]
    return prompts[fact.answer % len(prompts)]
