Add fuzzy searching ?

S3 FILE formart for resp
rep_id
    | -images
    | -manifestos
    | -cases
    | -any other file types

Notifications (Email, SMS, Push)
Add content type to metadata  ?
Add encoding to metadata utf-8/ascii etc ? use it to decode ?

implement monitor_progress --- > for file upload /download

Add serializer validity checks
if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


Hide users-swagger for external

Move from manage.py startup to proper production startup

Add AWS restrictions in scopes when pulling images i.e can pull only pro pic vs can pull all images

Confirm date params for groups and permissions


Switch from hardcoding URLs to using django url reverse for test
