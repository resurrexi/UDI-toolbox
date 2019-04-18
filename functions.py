def convert_instance(digits):
    """Convert instance of digits to string."""
    if isinstance(digits, int):
        return str(digits)
    elif isinstance(digits, str):
        return digits
    else:
        raise ValueError("Unrecognizable format, expecting digits")


def calc_check_digit(digits):
    """Calculate check digit given digits."""
    digits = convert_instance(digits)

    sum = 0
    for idx, digit in enumerate(reversed(digits)):
        if (idx + 1) % 2 == 0:
            sum += int(digit)
        else:
            sum += int(digit) * 3

    rightmost = str(sum)[-1]

    if rightmost == '0':
        return '0'
    else:
        return str(10 - int(rightmost))


def check_digit_validator(digits):
    """Validate check digit given digits."""
    digits = convert_instance(digits)

    leftpart = str(digits)[:-1]
    rightmost = str(digits)[-1]
    check_digit = calc_check_digit(leftpart)

    if check_digit == rightmost:
        return True
    else:
        return False


def generate_device_id(row, gs1, shelf=False, start=0, zeropad=3):
    """Generate unique device id."""
    device_id = '1' + str(gs1) + str(row.name + start).zfill(zeropad)
    if shelf is True:
        device_id = '3' + str(gs1) + str(row.name + start).zfill(zeropad)
    return device_id + calc_check_digit(device_id)
