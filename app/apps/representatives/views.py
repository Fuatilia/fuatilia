import os
import traceback
from app.apps.representatives.models import Representative
from app.apps.representatives.serializers import RepresentativeCreationSerializer
from app.utils.enum_utils import FileType
from rest_framework.generics import CreateAPIView
from app.utils.file_utils.generic_file_utils import file_upload

# Create your views here.


class CreateRepresenatative(CreateAPIView):
    async def post(self, request):
        create_body = request.data
        data_to_initialize_represenatative = {
            "full_name": create_body.get("full_name"),
            "position": create_body.get("position"),
            "position_type": create_body.get("position_type"),
            "house": create_body.get("house"),
            "area_represented": create_body.get("area_represented"),
            "phone_number": create_body.get("phone_number"),
            "gender": create_body.get("gender"),
            "representation_summary": create_body.get("representation_summary"),
        }

        try:
            print(
                "Representative creation with details :: ",
                data_to_initialize_represenatative,
            )
            validated_data = RepresentativeCreationSerializer(
                **data_to_initialize_represenatative
            )
            response_data = RepresentativeCreationSerializer.create(validated_data)

            metadata = {
                "rep_id": response_data["id"],
                "creation_date": response_data["created_at"].strftime(
                    "%d/%m/%Y %H:%M:%S"
                ),
                "source": create_body.get("image_source"),
                "image_type": create_body.get("image_data_type"),
                "use": "For representative image/thumbnail",
                "representative_name": response_data["full_name"],
                # 'content_type':
            }
            if response_data["status_code"] in [202, 200]:
                reps_data_bucket_name = os.environ.get("REPS_DATA_BUCKET_NAME")
                file_name = "profile_image.jpeg"

                print("Initiating file upload --- > to S3")
                if create_body.get("image_data_type") == "BASE64_ENCODING":
                    # File path should allow for replacement of images
                    s3_upload_response = await file_upload(
                        reps_data_bucket_name,
                        FileType.PROFILE_IMAGE,
                        file_name,
                        create_body.get("image_data"),
                        id=response_data["id"],
                        metadata=metadata,
                    )

                    if s3_upload_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                        image_url = f's3://{reps_data_bucket_name}/{response_data["id"]}/images/{file_name}'
                        response = Representative.asave(
                            {"id": response_data["id"], "image_url": image_url}
                        )

            return response

        except Exception as e:
            traceback.print_exc()
            return {"error": e.__repr__()}
