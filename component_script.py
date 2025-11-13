"""Grasshopper Python component script for architectural dimensions.

Input parameters expected by the component:

``length_in_inches`` (float)
    The measurement to convert, expressed in inches.

``precision_step`` (float)
    The rounding increment in inches.  Typical values are 1, 0.5, 0.25, 0.125,
    0.0625, and so on.

Output parameter produced by the component:

``dimension`` (text)
    The formatted architectural dimension string.
"""

from grasshopper_dimension import format_architectural_dimension


if length_in_inches is None or precision_step is None:
    dimension = (
        "Waiting for inputs: "
        f"length_in_inches={length_in_inches!r}, precision_step={precision_step!r}"
    )
else:
    try:
        dimension = format_architectural_dimension(length_in_inches, precision_step)
    except ValueError as exc:  # Invalid precision supplied
        dimension = (
            f"Error: {exc}\n"
            f"length_in_inches={length_in_inches!r}, precision_step={precision_step!r}"
        )
