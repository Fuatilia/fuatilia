from rest_framework import serializers


def add_request_data_to_span(span, request):
    # Not having a generic span incase there is need to change the span to something else
    # apart from what is the current span
    span.set_attribute("request.body", f"{request.data}")
    span.set_attribute("request.params", f"{request.GET.dict()}")

    return


class GenericFilterSerilizer(serializers.Serializer):
    created_at_start = serializers.DateTimeField(
        required=False, help_text="Start of date range filter for creation date"
    )
    created_at_end = serializers.DateTimeField(
        required=False, help_text="End of date range filter for creation date"
    )
    updated_at_start = serializers.DateTimeField(
        required=False, help_text="End of date range filter for update date"
    )
    updated_at_end = serializers.DateTimeField(
        required=False, help_text="End of date range filter for update date"
    )
    page = serializers.IntegerField(default=1)
    items_per_page = serializers.IntegerField(default=10)
