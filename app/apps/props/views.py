import logging
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema
from apps.generics.error_handler import process_error_response
from apps.generics.general import add_request_data_to_span
from apps.props.models import FAQ, Config
from apps.props import serializers
from rest_framework.response import Response
from rest_framework import status
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
logger = logging.getLogger("app_logger")


class CreateOrUpdateConfig(GenericAPIView):
    serializer_class = serializers.ConfigFetchSerializer

    @extend_schema(
        tags=["Configs"],
        request={"application/json": serializers.ConfigCreationSerializer},
        responses={201: serializers.ConfigFetchSerializer},
    )
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            logger.info(f"Config creation with details :: {request.data}")

            config_serializer = serializers.ConfigCreationSerializer(data=request.data)

            if config_serializer.is_valid():
                resp = config_serializer.save()
                return Response(
                    data=self.serializer_class(resp).data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    data=config_serializer.errors,
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            return process_error_response(e)


class FilterConfigs(GenericAPIView):
    serializer_class = serializers.ConfigFetchSerializer

    @extend_schema(
        tags=["Configs"],
        # Re-using the creation Body serlizer
        parameters=[serializers.FilterConfigsBody],
    )
    def get(self, request):
        span = trace.get_current_span()
        add_request_data_to_span(span, request)
        return self.get_queryset()

    def get_queryset(self):
        try:
            filter_params = {}

            if self.request.GET.get("name"):
                filter_params["name__contains"] = self.request.GET.get("name")
            if self.request.GET.get("value"):
                filter_params["value__contains"] = self.request.GET.get("value")
            if self.request.GET.get("created_by"):
                filter_params["created_by"] = self.request.GET.get("created_by")
            if self.request.GET.get("created_at_start"):
                filter_params["created_at__gte"] = self.request.GET.get(
                    "created_at_start"
                )
            if self.request.GET.get("created_at_end"):
                filter_params["created_at__lte"] = self.request.GET.get(
                    "created_at_end"
                )
            if self.request.GET.get("updated_at_start"):
                filter_params["updated_at__gte"] = self.request.GET.get(
                    "updated_at_start"
                )
            if self.request.GET.get("updated_at_end"):
                filter_params["updated_at__lte"] = self.request.GET.get(
                    "updated_at_end"
                )

            page = int(self.request.GET.get("page", "1"))
            items_per_page = int(self.request.GET.get("items_per_page", "10"))
            offset = (page - 1) * items_per_page

            queryset = Config.objects.filter(**filter_params)[
                offset : (offset + items_per_page)
            ]

            return Response(
                {
                    "data": self.serializer_class(queryset, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": e.__str__()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GUDConfig(GenericAPIView):
    serializer_class = serializers.ConfigFetchSerializer

    @extend_schema(tags=["Configs"], responses={200: "Succesful"})
    def get(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            config = Config.objects.get(pk=kwargs.get("id"))
            return Response(
                data=self.serializer_class(config).data, status=status.HTTP_200_OK
            )

        except Exception as e:
            return process_error_response(e)

    @extend_schema(tags=["Configs"], responses={204: "Config succesfully deleted"})
    def delete(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            config = Config.objects.get(pk=kwargs.get("id"))
            config.delete()
            return Response(
                data={"message": "Config succesfully deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as e:
            return process_error_response(e)

    @extend_schema(
        tags=["Configs"],
        request={"application/json": serializers.ConfigUpdateSerializer},
        responses={200: serializers.ConfigFetchSerializer},
    )
    def patch(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            logger.info(f"Config update with details :: {request.data}")

            config_serializer = serializers.ConfigUpdateSerializer(data=request.data)
            if config_serializer.is_valid():
                config_to_update = Config.objects.get(pk=kwargs.get("id"))
                config_serializer.update(
                    config_to_update, config_serializer.validated_data
                )
                return Response(
                    data=self.serializer_class(config_to_update).data,
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data=config_serializer.errors,
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            return process_error_response(e)


# ==============================================
# ==================== FAQ =====================
# ==============================================
class CreateFAQ(GenericAPIView):
    serializer_class = serializers.FAQFetchSerializer

    @extend_schema(
        tags=["FAQs"],
        request={"application/json": serializers.FAQCreationSerializer},
        responses={201: serializers.FAQFetchSerializer},
    )
    def post(self, request):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            logger.info(f"FAQ creation with details :: {request.data}")

            faq_serializer = serializers.FAQCreationSerializer(data=request.data)

            if faq_serializer.is_valid():
                resp = faq_serializer.save()
                return Response(
                    data=self.serializer_class(resp).data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    data=faq_serializer.errors,
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            return process_error_response(e)


class FilterFAQs(GenericAPIView):
    serializer_class = serializers.FAQFetchSerializer

    @extend_schema(tags=["FAQs"], parameters=[serializers.FilterFAQsBody])
    def get(self, request):
        span = trace.get_current_span()
        add_request_data_to_span(span, request)

        return self.get_queryset()

    def get_queryset(self):
        try:
            filter_params = {}

            if self.request.GET.get("faq"):
                filter_params["faq__contains"] = self.request.GET.get("faq")
            if self.request.GET.get("answer"):
                filter_params["answer__contains"] = self.request.GET.get("answer")
            if self.request.GET.get("created_by"):
                filter_params["created_by"] = self.request.GET.get("created_by")
            if self.request.GET.get("created_at_start"):
                filter_params["created_at__gte"] = self.request.GET.get(
                    "created_at_start"
                )
            if self.request.GET.get("created_at_end"):
                filter_params["created_at__lte"] = self.request.GET.get(
                    "created_at_end"
                )
            if self.request.GET.get("updated_at_start"):
                filter_params["updated_at__gte"] = self.request.GET.get(
                    "updated_at_start"
                )
            if self.request.GET.get("updated_at_end"):
                filter_params["updated_at__lte"] = self.request.GET.get(
                    "updated_at_end"
                )

            page = int(self.request.GET.get("page", "1"))
            items_per_page = int(self.request.GET.get("items_per_page", "10"))
            offset = (page - 1) * items_per_page

            queryset = FAQ.objects.filter(**filter_params)[
                offset : (offset + items_per_page)
            ]

            return Response(
                {
                    "data": self.serializer_class(queryset, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return process_error_response(e)


class GUDFAQ(GenericAPIView):
    serializer_class = serializers.FAQFetchSerializer

    @extend_schema(tags=["FAQs"], responses={200: "Succesful"})
    def get(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            faq = FAQ.objects.get(pk=kwargs.get("id"))
            return Response(
                data=self.serializer_class(faq).data, status=status.HTTP_200_OK
            )

        except Exception as e:
            return process_error_response(e)

    @extend_schema(tags=["FAQs"], responses={204: "FAQ succesfully deleted"})
    def delete(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            faq = FAQ.objects.get(pk=kwargs.get("id"))
            faq.delete()
            return Response(
                data={"message": "FAQ succesfully deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as e:
            return process_error_response(e)

    @extend_schema(
        tags=["FAQs"],
        request={"application/json": serializers.FAQUpdateSerializer},
        responses={200: serializers.FAQFetchSerializer},
    )
    def patch(self, request, **kwargs):
        try:
            span = trace.get_current_span()
            add_request_data_to_span(span, request)

            logger.info(f"FAQ update with details :: {request.data}")

            faq_serializer = serializers.FAQUpdateSerializer(data=request.data)
            if faq_serializer.is_valid():
                faq_to_update = FAQ.objects.get(pk=kwargs.get("id"))
                faq_serializer.update(faq_to_update, faq_serializer.validated_data)
                return Response(
                    data=self.serializer_class(faq_to_update).data,
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data=faq_serializer.errors,
                    status=status.HTTP_417_EXPECTATION_FAILED,
                )

        except Exception as e:
            return process_error_response(e)
