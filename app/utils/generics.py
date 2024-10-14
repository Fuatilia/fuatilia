def add_request_data_to_span(span, request):
    # Not having a generic span incase there is need to change the span to something else
    # apart from what is the current span
    span.set_attribute("request.body", f"{request.data}")
    span.set_attribute("request.params", f"{request.GET.dict()}")

    return


def add_string_data_to_span(span, span_string: str, ref: str):
    span.set_attribute(ref, span_string)
    return
