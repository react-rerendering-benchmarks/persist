from altair import (
    Chart,
    ConcatChart,
    FacetChart,
    FieldName,
    HConcatChart,
    LayerChart,
    RepeatChart,
    Tooltip,
    TopLevelSpec,
    Undefined,
    VConcatChart,
)
from altair.utils.core import parse_shorthand

spec_type_chart = [RepeatChart, FacetChart]

subchart_prop_map = {
    Chart: None,
    ConcatChart: "concat",
    HConcatChart: "hconcat",
    VConcatChart: "vconcat",
    LayerChart: "layer",
    RepeatChart: "spec",
    FacetChart: "spec",
}


def process_recursive_subcharts(chart: TopLevelSpec, fn_to_apply, *args, **kwargs):
    _type = type(chart)

    if _type not in subchart_prop_map:
        raise Exception(f"Unexpected chart type: {_type}")

    subchart_prop = subchart_prop_map[_type]

    chart = fn_to_apply(chart, *args, **kwargs)

    if subchart_prop is not None:
        subchart_value = getattr(chart, subchart_prop, None)

        if subchart_value is None:
            raise Exception(f"Instance of {_type} is missing property {subchart_prop}")

        if _type in spec_type_chart:
            subchart_value = process_recursive_subcharts(
                chart=subchart_value, fn_to_apply=fn_to_apply, *args, **kwargs
            )

        elif isinstance(subchart_value, list):
            for idx, subchart in enumerate(subchart_value):
                subchart_value[idx] = process_recursive_subcharts(
                    chart=subchart, fn_to_apply=fn_to_apply, *args, **kwargs
                )

        setattr(chart, subchart_prop, subchart_value)

    if chart is None:
        return "Argument 'fn_to_apply' should be a function and should return the modified chart. It seems to return 'None' instead."
    return chart


""" Encoding Values
    - Field Encoding
      {
        "field": field name (optional if agg is count),
        "type": "quantitative", "nominal", "ordinal", "temporal", "geojson"
        "aggregate": any agg operation; 
        "bin": When column is quantitative and other operation is aggregate
      }
    - Datum Encoding
      {
        datum: valid value from dataset
      }
    - Value Encoding
      {
        value: any value
      }
"""


def add_new_nominal_encoding(chart, field_name):
    encoding_string = f"{field_name}:N"
    encoding = getattr(chart, "encoding", Undefined)

    if encoding is Undefined:
        return chart

    chart = add_tooltip_encoding(chart, encoding_string)

    color_encoding = getattr(encoding, "color", Undefined)

    if color_encoding is Undefined:
        return chart.encode(color=encoding_string)
    elif is_conditional_encoding(color_encoding):
        if hasattr(color_encoding._kwds["condition"], "value"):
            color_encoding._kwds["condition"].value = Undefined
            color_encoding._kwds["condition"].field = FieldName(field_name)
            setattr(chart.encoding, "color", color_encoding)
            return chart

    shape_encoding = getattr(encoding, "shape", Undefined)

    if hasattr(chart, "mark") and shape_encoding is Undefined:
        mark = chart.mark

        if hasattr(mark, "type"):
            mark = mark.type

        if mark != "point":
            return chart

        return chart.encode(shape=encoding_string)

    print(f"Encoded '{field_name}' as tooltip only")

    return chart


def add_new_nominal_encoding_recursive(chart, field_name):
    return process_recursive_subcharts(chart, add_new_nominal_encoding, field_name)


def check_encodings_for_utc(chart):
    encoding = getattr(chart, "encodings", Undefined)

    if encoding is not Undefined:
        encoding = encoding.to_dict()

        for channel, enc in encoding.items():
            enc_str = str(enc)
            if "timeUnit" in enc_str and "utc" not in enc_str:
                raise Exception(
                    f"Encoding for '{channel}' possibly using `timeUnit` without `utc` specification. Please use `utc` time formats for compatibility with interactions. E.g use `utcyear` or `utcmonth` instead of `year` or `month`.\n Provided encoding: {v}"
                )

    return chart


def check_encodings_for_utc_recursive(chart):
    return process_recursive_subcharts(chart, check_encodings_for_utc)


def add_tooltip_encoding(chart, field_encoding):
    """
    Set tooltip encoding of chart to supplied field_encoding
    """
    if hasattr(chart, "encoding"):
        encoding = getattr(chart.encoding, "tooltip", Undefined)

        if encoding is Undefined:
            return chart.encode(tooltip=[field_encoding])

        if isinstance(encoding, list):
            encoding.append(field_encoding)
            return chart.encode(tooltip=encoding)

        if is_shorthand(encoding):
            encoding = [encoding, Tooltip(field_encoding)]

    return chart


def add_tooltip_encoding_recursive(chart, field):
    chart = process_recursive_subcharts(chart, add_tooltip_encoding, field)
    return chart


def is_shorthand(encoding):
    return hasattr(encoding, "shorthand")


def get_parsed_encoding(encoding):
    if is_shorthand(encoding):
        return parse_shorthand(encoding.shorthand)
    return encoding


def is_field_encoding(encoding):
    return hasattr(encoding, "field")


def is_aggregate_encoding(encoding):
    return hasattr(encoding, "aggregate")


def is_quantitative(encoding):
    return getattr(encoding, "type", None) == "quantitative"


def is_nominal(encoding):
    return getattr(encoding, "type", None) == "nominal"


def is_ordinal(encoding):
    return getattr(encoding, "type", None) == "ordinal"


def is_temporal(encoding):
    return getattr(encoding, "type", None) == "temporal"


def is_binned(encoding):
    return hasattr(encoding, "bin")


def is_datum_encoding(encoding):
    return hasattr(encoding, "datum")


def is_conditional_encoding(encoding):
    return hasattr(encoding, "condition")


def is_value_encoding(encoding):
    return hasattr(encoding, "value")


def is_value_only_encoding(encoding):
    return not is_conditional_encoding(encoding) and is_value_encoding(encoding)
