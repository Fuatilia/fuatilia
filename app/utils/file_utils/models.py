from rest_framework import serializers
from utils.enum_utils import FileTypeTextChoices


class GenericFileUploadSerilizer(serializers.Serializer):
    file_source = serializers.CharField(
        required=False, help_text="Where the file was gotten from e.g Gok Site"
    )
    file_type = serializers.ChoiceField(choices=FileTypeTextChoices.choices)
    base64_encoding = serializers.CharField(
        default="ewogICAgIlJlcHJlc2VudGF0aXZl\
                IG9uZSI6ICJZRVMiLAogICAgIlJlcHJlc2VudGF0aXZlIHR3\
                byI6ICJOTyIsCiAgICAiUmVwcmVzZW50YXRpdmUgdGhyZWUiOi\
                AiQUJTRU5UIiwKICAgICJSZXByZXNlbnRhdGl2ZSBmb3VyIjog\
                Ik4vQSIsCiAgICAiUmVwcmVzZW50YXRpdmUgZml2ZSI6ICJJTk\
                FVRElCTEUiCn0="
    )
    file_extension = serializers.CharField(default=".jpeg")
    file_name = serializers.CharField(default="IMAGE.jpeg")
    string_encoding_fmt = serializers.CharField(default="utf-8")
