from persist_ext.internals.data.idfy import idfy_dataframe
from persist_ext.internals.data.validate import (
    DEFAULT_PREPROCESS_FN,
    is_dataframe_or_url,
)


def prepare(df, preprocess_fn=DEFAULT_PREPROCESS_FN):
    df = is_dataframe_or_url(df, preprocess_fn)  # check if is valid dataframe
    df = idfy_dataframe(df)  # add id column

    return df
