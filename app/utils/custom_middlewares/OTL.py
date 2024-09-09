# OpenTelemetry Middlewares
import logging
from django.http import StreamingHttpResponse, HttpResponse, FileResponse
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
            if response.__class__ == StreamingHttpResponse:
                span.set_attribute("response.class", "StreamingHttpResponse")
            elif response.__class__ == FileResponse:
                span.set_attribute("response.class", "FileResponse")
            elif response.__class__ == HttpResponse:
                # Prometheus and Django URLs using HttpResponses
                span.set_attribute("response.class", "HttpResponse")
                span.set_attribute("response.content", f"{response.content}")

            else:
                span.set_attribute("response.body", f"{response.data}")

        except Exception as e:
            logger.exception(e)
            span.set_attribute("response.error", f"{e.__str__()}")

        span.set_attribute("response.status", f"{response.status_code}")
        span.set_attribute("response.headers", f"{response.headers}")

        response.headers["span-id"] = "{trace:032x}".format(
            trace=span.get_span_context().span_id
        )
        response.headers["trace-id"] = "{span:016x}".format(
            span=span.get_span_context().trace_id
        )

        return response
