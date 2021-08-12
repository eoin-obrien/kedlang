def to_ked_string(value="") -> str:
    if isinstance(value, list):
        return [to_ked_string(element) for element in value]

    if value is None:
        return "nuttin"
    elif isinstance(value, bool):
        return "gospel" if value else "bull"
    elif isinstance(value, float):
        return str(int(value)) if value.is_integer() else str(value)
    return str(value)


def to_ked_number(value=None) -> float:
    if value is None:
        return 0
    try:
        return float(value)
    except ValueError:
        return float("nan")


def to_ked_boolean(value=None) -> bool:
    return bool(value)
