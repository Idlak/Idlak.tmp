This is a Rest API that allows registered users receive processed speech by sending a request.
The server only contains two databases for authorisation and information about voices.
The voices themselves are used from idlak, therefore the server is not usable alone and idlak has to be installed.

## Install server

To install the Rest server one must:

* Have python (preferably version >= 3.5) with pip installed
* And in the `idlak-server` directory
    * Run command `source setup-server.sh` to setup flask
    * Run command `flask run` to setup the database
    * Run command `flask run` to run the server
        * when the server is ran for the first time, the initial admin user will be created and it's details presented in format `<User userid:password:isadmin>`

Before installing and running the server make sure that the settings provided in config are correct, especially the current user and speech path.
If you are not debugging or testing the server set logging to 'INFO', no sensitive data will be logged.

## Run server

To run the already installed Rest server one must (if you haven't ran it after the installation):

* In the `idlak-server` directory
    * Run command `source venv\bin\activate`
    * Run command `flask run` to run on default host and port
    * OR run command `flask run --host=0.0.0.0 --port=80` to run on specific host and port

## Loading voices

In order for the users to get speech of any voice, the database must know about the voices and their location.
To set a voice up, the server must be installed and in the `idlak-server` directory a command has to be run:
```
./seed/addvoice.py -g female -n Anastasia -i abr -d ../idlak-egs/tts_tangle_idlak/s2/voices/ru/ru/abr_pmdl
```
the different information based on the voice must be provided: gender, name, id and tpdb directory
To remove voice information from the server, a command in the `idlak-server` directory has to be run:
```
./seed/removevoice.py -i abr
```
where the id of the voice has to be provided


Once the server has information of the voices, the user can access this information and get processed speech of these voices.

# API Documentation

## Authentication
**Retrieve an authentication token**

> **[ POST ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */auth*

Permissions: ```none```<br>
Authorization Header: ```none```<br>
Accepted content types: ```application/json```<br>
Arguments:

| Argument | Example | Required  | Description |
| -- | -- | -- | :-- |
| ```uid``` | ```userid``` | Required | User id for registered user |
| ```password``` | ```pass``` | Required | Password for registered user |

Response (```200 OK```):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1MzIxMDEyNDEsIm5iZiI6MTUzMjEwMTI0MSwiZXhwIjoxNTMyMTA0ODQxLCJzdWIiOiJhZG1pbiJ9.gxTh6ubxqb7lqSZnWnQeWCXOS9u6cJ7skMBUbm2gJiI"
}
```
Typical error response (```401 UNAUTHORIZED```):
```json
{
    "message": "Login details are incorrect"
}
```
## Users
**Retrieve a list of currently registered users.**<br>

> **[ GET ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */users*

Permissions: ```admin```<br>
Authorization Header: ```Bearer <access_token>```<br>
Response (```200 OK```):
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
Typical error response (```401 UNAUTHORIZED```):
```json
{
    "message": "Access token is invalid"
}
```
---
**Create a new user account**

> **[ POST ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */users*

Permissions: ```admin```<br>
Authorization Header: ```Bearer <access_token>```<br>
Accepted content types: ```application/json```<br>
Arguments:

| Argument | Example | Required  | Description |
| -- | -- | -- | :-- |
| ```uid``` | ```userid``` | Optional | User id, generated randomly by default  |
| ```admin``` | ```true``` | Optional | Admin permissions - true/false (default: false) |

Response (```200 OK```):
```json
{
    "admin": true,
    "password": "e37bf8f6",
    "uid": "userid"
}
```
Typical error response (```422 UNPROCESSABLE ENTITY```):
```json
{
    "message": "User id already exists"
}
```
---
**Generate new password**

> **[ POST ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */users/`<uid>`/password*

Permissions: ```admin```<br>
Authorization Header: ```Bearer <access_token>```<br>
Response (```200 OK```):
```json
{
    "password": "621175b8"
}
```
Typical error response (```422 UNPROCESSABLE ENTITY```):
```json
{
    "message": "User does not exist"
}
```
---
**Toggle users admin status**

> **[ POST ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */users/`<uid>`/admin*

Permissions: ```admin```<br>
Authorization Header: ```Bearer <access_token>```<br>
Response (```200 OK```):
```json
{
    "admin": true,
    "uid": "userid"
}
```
Typical error response (```422 UNPROCESSABLE ENTITY```):
```json
{
    "message": "User does not exist"
}
```
---
**Delete a user**

> **[ DELETE ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */users/`<uid>`*

Permissions: ```admin```<br>
Authorization Header: ```Bearer <access_token>```<br>
Response (```200 OK```):
```json
{
    "message": "User 'userid' has been deleted"
}
```
Typical error response (```422 UNPROCESSABLE ENTITY```):
```json
{
    "message": "User does not exist"
}
```
## Languages
**Lists available languages**

> **[ GET ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */languages*

Permissions: ```none```<br>
Authorization Header: ```none```<br>
Response (```200 OK```):
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

> **[ GET ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */languages/`<lang_iso>`/accents*

Permissions: ```none```<br>
Authorization Header: ```none```<br>
Response (```200 OK```):
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
Typical error response (```404 NOT FOUND```):
```json
{
    "message": "Language could not be found"
}
```
## Voices
**Get available voices**

> **[ GET ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */voices*

Permissions: ```none```<br>
Authorization Header: ```none```<br>
Accepted content types: ```application/json```<br>
Arguments:

| Argument | Example | Required  | Description |
| -- | -- | -- | :-- |
| ```language``` | ```en``` | Optional | Language code in ISO 2 letter format |
| ```accent``` | ```gb``` | Optional | Accent code in 2 letter format |
| ```gender``` | ```female``` | Optional | Voice gender - male/female  |

Response (```200 OK```):
```json
{
    "voices" : [
        {
              "voice_id": "voiceid",
              "language": "en",
              "accent": "gb",
              "gender": "female",
              "name": "voice",
              "...": "..."
        },
        "..."
    ]
}
```
Typical error response (```204 NO CONTENT```):
```json
{
    "message": "No voices were found"
}
```
---
**Get voice details**

> **[ GET ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */voices/`<voice_id>`*

Permissions: ```none```<br>
Authorization Header: ```none```<br>
Response (```200 OK```):
```json
{
      "voice_id": "voiceid",
      "language": "en",
      "accent": "gb",
      "gender": "female",
      "name": "voice",
      "...": "..."
}
```
Typical error response (```404 NO CONTENT```):
```json
{
    "message": "Voice could not be found"
}
```

## Speech Synthesis
**Synthesise speech**

> **[ POST ]** ‏‏‎  ‏‏‎  ‏‏‎ | ‏‏‎  ‏‏‎  ‏‏‎ */speech*

Permissions: ```none```<br>
Authorization Header: ```Bearer <access_token>```<br>
Accepted content types: ```application/json```<br>
Arguments:

| Argument | Example | Required  | Description |
| -- | -- | -- | :-- |
| ```voice_id``` | ```voiceid``` | Required | Voice ID |
| ```audio_format``` | ```mp3``` | Optional | Audio file format - wav/ogg/mp3 (default: wav) |
| ```text``` | ```Hello``` | Required | Text input for speech synthesis |

Response (```200 OK```): Streamed audio file.<br>
Typical error response (```400 BAD REQUEST```):
```json
{
      "message": "Voice could not be found"
}
```
## Error Codes and Messages
| Status Code | Possible outcome |
| -- | -- |
| ```204 No Content``` | The query was successful but gave no results |
| ```400 Bad Request``` | Voice could not be found, the voice id is incorrect |
| ```401 Unauthorized``` | Wrong login details<br> Access token has expired / is invalid<br> User doesn't have permissions required to access (admin permissions)|
| ```404 Not Found``` | Requested data could not be found. |
| ```422 Unprocessable Entity``` | User already exists<br> User does not exist<br> User is the only admin, there must be at least one admin in the system |
| ```501 Not Implemented``` | The endpoint is not implemented yet |
| ```500 Internal Server Error``` | Something went wrong on the server, the admins should be informed about the error |


Look at the README: [https://github.com/Idlak/idlak/tree/master/idlak-server](https://github.com/Idlak/idlak/tree/master/idlak-server)
