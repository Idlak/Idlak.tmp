
# Idlak Speech Synthesis Server

This server runs an RESTful API based on Python Flask.

When setting up the server a single user with Admin permissions is created.



# API Documentation

## Authentication
**Retrieve an authentication token**
| [ POST ] | */auth* |
| - | - |
Permissions: ```none```
Authorization Header: ```none```
Accepted content types: ```application/json```
Arguments:
| Argument | Example | Required  | Description |
| -- | -- | -- | :-- |
| ```uid``` | ```userid``` | Required | User id for registered user |
| ```password``` | ```pass``` | Required | Password for registered user |
Response (200 ok):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1MzIxMDEyNDEsIm5iZiI6MTUzMjEwMTI0MSwiZXhwIjoxNTMyMTA0ODQxLCJzdWIiOiJhZG1pbiJ9.gxTh6ubxqb7lqSZnWnQeWCXOS9u6cJ7skMBUbm2gJiI"
}
```
Typical error response (401 unauthorized):
```json
{
    "message": "Login details are incorrect"
}
```
## Users

**Retrieve a list of currently registered users.**
| [ GET ] | */users* |
| - | - |
Permissions: ```admin```
Authorization Header: ```Bearer <access_token>```
Response (200 OK):
```json
{
    "users": [
        {
            "admin": true,
            "id": "admin"
        },
        {
            "admin": false,
            "id": "userid"
        }
    ]
}
```
Typical error response (401 unauthorized):
```json
{
    "message": "Access token is invalid"
}
```
---
**Create a new user account**
| [ POST ] | */users* |
| - | - |
Permissions: ```admin```
Authorization Header: ```Bearer <access_token>```
Accepted content types: ```application/json```
Arguments:
| Argument | Example | Required  | Description |
| -- | -- | -- | :-- |
| ```uid``` | ```userid``` | Optional | User id, generated randomly by default  |
| ```admin``` | ```true``` | Optional | Admin permissions - true/false (default: false) |
Response (200 OK):
```json
{
    "admin": true,
    "password": "e37bf8f6",
    "uid": "userid"
}
```
Typical error response (422 unprocessable entity):
```json
{
    "message": "User id already exists"
}
```
---
**Generate new password**
| [ POST ] | */users/`<uid>`/password* |
| - | - |
Permissions: ```admin```
Authorization Header: ```Bearer <access_token>```
Response (200 OK):
```json
{
    "password": "621175b8"
}
```
Typical error response (422 unprocessable entity):
```json
{
    "message": "User does not exist"
}
```
---
**Delete a user**
| [ DELETE ] | */users/`<uid>`* |
| - | - |
Permissions: ```admin```
Authorization Header: ```Bearer <access_token>```
Response (200 OK):
```json
{
    "message": "User 'userid' has been deleted"
}
```
Typical error response (422 unprocessable entity):
```json
{
    "message": "User does not exist"
}
```
## Languages
**Lists available languages**
| [ GET ] | */languages* |
| - | - |
Permissions: ```none```
Authorization Header: ```none```
Response (200 OK):
```json
{
    "languages": [
        "en",
        "it",
        "es"
    ]
}
```

**Lists available accents of a language**
| [ GET ] | */languages/`<lang_iso>`/accents* |
| - | - |
Permissions: ```none```
Authorization Header: ```none```
Response (200 OK):
```json
{
    "accents": [
        "ca",
        "gb",
        "us"
    ],
    "language": "en"
}
```
Typical error response (404 not found):
```json
{
    "message": "Language could not be found"
}
```
## Voices

**Get available voices**
| [ GET ] | */voices* |
| - | - |
Permissions: ```none```
Authorization Header: ```none```
Accepted content types: ```application/json```
Arguments:
| Argument | Example | Required  | Description |
| -- | -- | -- | :-- |
| ```language``` | ```en``` | Optional | Language code in ISO 2 letter format |
| ```accent``` | ```gb``` | Optional | Accent code in 2 letter format |
| ```gender``` | ```female``` | Optional | Voice gender - male/female  |
Response (200 OK):
```json
{
    'voices' : [
        {
              "voice_id": "voiceid",
              "language": "en",
              "accent": "gb",
              "gender": "female",
              "name": "voice",
              ...
        },
        ...
    ]
}
```
Typical error response (204 no content):
```json
{
    "message": "No voices were found"
}
```
---
**Get voice details**
| [ GET ] | */voices/`<voice_id>`* |
| - | - |
Permissions: ```none```
Authorization Header: ```none```
Response (200 OK):
```json
{
      "voice_id": "voiceid",
      "language": "en",
      "accent": "gb",
      "gender": "female",
      "name": "voice",
      ...
}
```
Typical error response (404 no content):
```json
{
    "message": "Voice could not be found"
}
```

## Speech Synthesis
**Synthesise speech**
| [ POST ] | */speech* |
| - | - |
Permissions: ```none```
Authorization Header: ```Bearer <access_token>```
Accepted content types: ```application/json```
Arguments:
| Argument | Example | Required  | Description |
| -- | -- | -- | :-- |
| ```voice_id``` | ```voiceid``` | Required | Voice ID |
| ```streaming``` | ```true``` | Optional | Audio file streaming - true/false (default: false) |
| ```audio_format``` | ```mp3``` | Optional | Audio file format - wav/ogg/mp3 (default: wav) |
| ```text``` | ```Hello``` | Required | Text input for speech synthesis |

Response (501 not implemented):
```json
{
      "message": "Not implemented yet"
}
```
