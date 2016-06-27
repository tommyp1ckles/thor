# Thor

## Set env variables.

`TWILIO_SID`: Twilio account SID.

`TWILIO_TOKEN`: Twilio API access token.

`TWILIO_NUMBER`: Twilio number to send from.

`THOR_API_KEY`: The Thor API access token. For example generate this by doing:

`export THOR_API_KEY=$(openssl rand -base64 32)`

## Init thor database.
`sqlite3 thor.db < schema.sql`
