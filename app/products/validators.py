def phone_number_all_numeric(value: str):
    if value:
        if value.isnumeric():
            return value
        raise ValueError("Phone number should contain only numbers.")
    return value
