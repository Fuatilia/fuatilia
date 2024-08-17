#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider

from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from opentelemetry import trace


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")
    try:
        from django.core.management import execute_from_command_line

        TRACING_EXPORTER_ENDPOINT = f'{os.getenv("TRACING_EXPORTER_ENDPOINT")}'
        resource = Resource(attributes={SERVICE_NAME: "fuatilia-api-tracer"})

        trace_provider = TracerProvider(resource=resource)
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=TRACING_EXPORTER_ENDPOINT)
        )

        trace_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(trace_provider)

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
