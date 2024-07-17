Add CI/CD , linting etc
Fix filters for 'get' to allow pagination from page param
Add signed url option for uploads
Add lIMITs for count in get functions

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


Permissins Format
[
    {
        "entity": "User",
        "scope": "Data",
        "permission": "Read",
        "effect": "Allow",
    },
    {
        "entity": "User",
        "scope": "List",
        "permission": "Read",
        "effect": "Allow",
    },
    {
        "entity": "User",
        "scope": "Data",
        "permission": "Update.Create",
        "effect": "Allow",
    },
    {
        "entity": "User",
        "scope": "List",
        "permission": "Update.Approve",
        "effect": "Allow",
    },
]
