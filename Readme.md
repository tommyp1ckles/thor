# Thor

## Get Dependencies
`pip install -r requirements.txt`

## Set env variables.
`TWILIO_SID`: Twilio account SID.
`TWILIO_TOKEN`: Twilio API access token.
`TWILIO_NUMBER`: Twilio number to send from.
`THOR_API_KEY`: The Thor API access token. For example generate this by doing:

`export THOR_API_KEY=$(openssl rand -base64 32)`

## Init thor database.
`sqlite3 thor.db < schema.sql`

## Usage
Give exec permissions on thor: `chmod +x thor.py`

And run thor `/thor.py`

## API

### Create User
`POST`: `/api/users`

```
{
	"name": "<name>",
	"email": "<email>",
	"phone": "<phone>",
	"defcon": <defcon>,
	"token": "<THOR_API_TOKEN>"
}
```

### Update User
`PUT`: `/api/users`

```
{
	"id": "<user_id>",
	"name": "<name>*",
	"email": "<email>*",
	"phone": "<phone>*",
	"defcon": <defcon>*,
	"token": "<THOR_API_TOKEN>"
}
```

### Send Event
`POST`: `/api/events`

```
{
	"node": "<node>",
	"defcon": <defcon>,
	"content": "<content>",
}
```
