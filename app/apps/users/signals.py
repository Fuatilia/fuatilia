import logging
import django.dispatch
from django.contrib.auth.models import Group
from opentelemetry import trace
from utils.generics import add_string_data_to_span

logger = logging.getLogger("app_logger")
tracer = trace.get_tracer(__name__)

# Dispatcher to assign role after user creation
role_assignment_signal = django.dispatch.Signal()


@django.dispatch.receiver(role_assignment_signal)
def add_role_to_app_or_user(sender, **kwargs):
    span = trace.get_current_span()
    add_string_data_to_span(
        span,
        f"App/User signal for creation --> Role  : {kwargs['role_name']} , User : {kwargs['user']}",
        "user.role.creation",
    )

    userInstance = kwargs["user"]
    logger.info(
        f"signal from {sender} initiated add_role_to_app_or_user for {userInstance.id} for role {kwargs['role_name']}"
    )
    group = Group.objects.get(name=kwargs["role_name"])
    userInstance.groups.add(group)

    logger.debug(
        f"Adding role {kwargs['role_name']} to user  {userInstance.id} ===> completed"
    )
