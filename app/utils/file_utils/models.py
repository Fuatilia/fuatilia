from rest_framework import serializers
from utils.enum_utils import FileTypeTextChoices


class GenericFileUploadSerilizer(serializers.Serializer):
    file_source = serializers.CharField(
        required=False, help_text="Where the file was gotten from e.g Gok Site"
    )
    file_type = serializers.ChoiceField(choices=FileTypeTextChoices.choices)
    base64_encoding = serializers.CharField()
    file_extension = serializers.CharField(default=".jpeg")
    file_name = serializers.CharField(default="IMAGE.jpeg")
    version = serializers.CharField(default="v1")
