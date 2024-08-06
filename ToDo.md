Fix auth  for user

Add fuzzy searching ?

S3 FILE formart for resp
rep_id
    | -images
    | -manifestos
    | -cases
    | -any other file types

Notifications (Email, SMS, Push)
Send image upload and processing to a queue?
Add content type to metadata  ?

implement monitor_progress --- > for file upload /download


Move picture uploads for representatives to a seperate endpoint
Or allow both but create server side event once upload is done



Remove image url from  response use the get file endpoint to get user image

Add serializer validity checks
if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
