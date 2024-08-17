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


Remove image url from  response use the get file endpoint to get user image or switch to image ID with image table ?

Add serializer validity checks
if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


Hide users-swagger for external

Add **kwargs to span and add span traces to all endpouints with **krgs (Get/Delete)
Update response with trace ID all endpoints ?

Move from manage.py startup to proper production startup
