# "shared.py" from libWiiPy by NinjaCheetah & Contributors
# https://github.com/NinjaCheetah/libWiiPy

def align_value(value, alignment=64):
    """Aligns the provided value to the set alignment (defaults to 64).

    Parameters
    ----------
    value : int
        The value to align.
    alignment : int
        The number to align to. Defaults to 64.

    Returns
    -------
    int
        The aligned value.
    """
    if (value % alignment) != 0:
        aligned_value = value + (alignment - (value % alignment))
        return aligned_value
    return value


def pad_bytes_stream(data, alignment=64):
    """Pads the provided bytes stream to the provided alignment (defaults to 64).

    Parameters
    ----------
    data : BytesIO
        The data to align.
    alignment : int
        The number to align to. Defaults to 64.

    Returns
    -------
    BytesIO
        The aligned data.
    """
    while (data.getbuffer().nbytes % alignment) != 0:
        data.write(b'\x00')
    return data
