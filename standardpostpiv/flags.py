from typing import List


def get_flag_names(flag_value, flag_meaning) -> List:
    """Return a list of flag names for a given flag value"""
    if flag_value == 0:
        return ['INACTIVE']

    flag_names = []

    for flagmeaning_value, flagmeaning_name in flag_meaning.items():
        if flag_value & flagmeaning_value:
            flag_names.append(flagmeaning_name)

    return flag_names
