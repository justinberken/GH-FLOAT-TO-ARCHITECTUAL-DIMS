"""Grasshopper architectural dimension formatting helper.

This module provides a single function, :func:`format_architectural_dimension`,
which converts a raw float measurement expressed in inches to an architectural
dimension string such as ``4 ft 6 1/2 in``.  The function is intended to be used
inside a Grasshopper Python component, but it can also be imported and used in
any regular Python environment.

Example
-------
>>> format_architectural_dimension(48.5, 0.125)
'4 ft 0 1/2 in'

The helper keeps its rounding behaviour aligned with the supplied precision
step.  Precision steps are expressed as the length, in inches, of the smallest
increment that should appear in the formatted dimension.  Typical values are
``1`` (nearest inch), ``0.5`` (nearest half inch), ``0.25`` (nearest quarter
inch), ``0.125`` (nearest eighth inch), and so on.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional


@dataclass(frozen=True)
class ArchitecturalDimension:
    """Container describing an architectural dimension.

    Attributes
    ----------
    feet:
        Whole feet component of the measurement.
    inches:
        Whole inches component of the measurement (always between 0 and 11).
    fraction:
        Optional fractional inch component expressed as a :class:`Fraction`.
    negative:
        Flag indicating whether the original measurement was negative.
    """

    feet: int
    inches: int
    fraction: Optional[Fraction]
    negative: bool = False

    def to_string(self) -> str:
        """Return a human-readable representation.

        Returns
        -------
        str
            A formatted string such as ``4 ft 6 1/2 in``.  The fractional part
            is omitted when it is equal to zero.
        """

        if not (self.feet or self.inches or self.fraction):
            return "0 ft"

        feet_part = f"{self.feet} ft"

        inch_components = []
        if self.inches:
            inch_components.append(str(self.inches))
        if self.fraction is not None:
            inch_components.append(f"{self.fraction.numerator}/{self.fraction.denominator}")

        inches_part = f" {' '.join(inch_components)} in" if inch_components else ""

        body = f"{feet_part}{inches_part}"
        return f"-{body}" if self.negative else body


def _normalise_precision_step(precision_step: float) -> float:
    if precision_step <= 0:
        raise ValueError("precision_step must be greater than zero")
    return precision_step


def format_architectural_dimension(length_in_inches: float, precision_step: float) -> str:
    """Format a floating-point measurement as an architectural dimension string.

    Parameters
    ----------
    length_in_inches:
        Measurement expressed in inches.  The function accepts positive or
        negative numbers and will return a string in feet, inches, and the
        closest fractional increment.
    precision_step:
        The smallest fractional increment to use during rounding, expressed in
        inches.  For example, ``0.125`` corresponds to 1/8" increments.  Values
        must be greater than zero.

    Returns
    -------
    str
        A string describing the formatted architectural dimension.
    """

    step = _normalise_precision_step(precision_step)

    negative = length_in_inches < 0
    measurement = abs(length_in_inches)

    feet = int(measurement // 12)
    inches = measurement - feet * 12

    rounded_inches = round(inches / step) * step

    # Handle rounding that carries into the next foot.
    if rounded_inches >= 12 - (step / 2):
        feet += 1
        rounded_inches = 0.0

    whole_inches = int(rounded_inches // 1)
    fractional_inches = rounded_inches - whole_inches

    # Convert the fractional component to the nearest rational representation
    # based on the provided precision step.
    if fractional_inches > 1e-9:
        denominator = max(int(round(1 / step)), 1)
        numerator = int(round(fractional_inches * denominator))
        fraction = Fraction(numerator, denominator)
        if fraction.numerator == fraction.denominator:
            whole_inches += 1
            fraction = None
    else:
        fraction = None

    # Compensate for inch overflow (e.g., 11 8/8" -> 12").
    if whole_inches >= 12:
        feet += whole_inches // 12
        whole_inches = whole_inches % 12

    architectural_dimension = ArchitecturalDimension(
        feet=feet,
        inches=whole_inches,
        fraction=fraction,
        negative=negative,
    )

    return architectural_dimension.to_string()


__all__ = ["format_architectural_dimension", "ArchitecturalDimension"]


if __name__ == "__main__":  # pragma: no cover - convenience demonstration
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("length", type=float, help="Length in inches to format")
    parser.add_argument(
        "precision",
        type=float,
        help="Precision step in inches (e.g. 0.125 for 1/8\")",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        print("\nExample: python grasshopper_dimension.py 48.5 0.125")
    else:
        args = parser.parse_args()
        print(format_architectural_dimension(args.length, args.precision))
