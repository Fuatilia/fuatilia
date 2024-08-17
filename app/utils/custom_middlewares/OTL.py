# OpenTelemetry Middlewares
import logging

from opentelemetry import trace


tracer = trace.get_tracer(__name__)

logger = logging.getLogger("app_logger")


class RequestInjectorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        span = trace.get_current_span()

        logger.info(request.headers)
        span.set_attribute("request.headers", f"{request.headers}")

        response = self.get_response(request)
        logger.info(response)

        try:
            span.set_attribute("response.body", f"{response.data}")

        except AttributeError:
            # Prometheus URLs using HttpResponses
            span.set_attribute("response.content", f"{response.content}")

        span.set_attribute("response.status", f"{response.status_code}")
        span.set_attribute("response.headers", f"{response.headers}")

        response.headers["span-id"] = span.get_span_context().span_id
        response.headers["trace-id"] = span.get_span_context().trace_id

        return response
