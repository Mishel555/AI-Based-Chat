JWT token (exp date: Thursday, June 15, 2023 21:09:50):

```shell
export $JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbm9ueW1vdXMiLCJleHAiOjE2ODY4NjMzOTB9.F9RdekWGK0wDcxhpWgb8QF8kyBEQBjpTtnuYYw9V0m8
```

Development UI endpoints:

```shell
URL=https://831x59eird.execute-api.us-east-1.amazonaws.com/dev-ui/
WS_URL=wss://pwid0kem89.execute-api.us-east-1.amazonaws.com/dev-ui/?x-jwt-token=$JWT
```

Send `start_chat` request:

```shell
curl -X POST -H "x-jwt-token: $JWT" $URL/validator/chat_session -d '{"ts": "2023-05-16T21:45:10.460757"}'
```

You will get the following response, which are `chat_id` and `chat_ts`:

```json
{
  "id": "d3641f32-72b7-4f7b-a87c-410f150a5040",
  "ts": "2023-05-19T16:45:09.111979+00:00"
}
```

Send `human_input` message over WebSocket, payload:

```json
{
  "action": "human_input",
  "x-jwt-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbm9ueW1vdXMiLCJleHAiOjE2ODY5MzM4OTd9.bng3ao51Ggx-Scs8VVDFr6PBtmChYYgYTfMO_mqWw48",
  "body": "{\"chat_id\":\"d3641f32-72b7-4f7b-a87c-410f150a5040\", \"chat_ts\": \"2023-05-19T16:45:09.111979+00:00\", \"ts\": \"2023-05-17T13:51:00.703323Z\", \"human_input\":\"The Earth revolves around the Sun, takes about 365.25 days for a full orbit, has a slightly tilted axis, and is the third planet from the Sun.\", \"extra\":\"some-extra-id\"}"
}
```

In the above message `body` is a serialized JSON of the following structure:

```json
{
  "chat_id": "d3641f32-72b7-4f7b-a87c-410f150a5040",
  "chat_ts": "2023-05-19T16:45:09.111979+00:00",
  "ts": "2023-05-17T13:51:00.703323Z",
  "human_input": "The Earth revolves around the Sun, takes about 365.25 days for a full orbit, has a slightly tilted axis, and is the third planet from the Sun.",
  "extra": "some-extra-id"
}
```

Messages will start arriving, which are:

Statement response:

```json
{
  "ts": "2023-05-19T16:46:24.709416+00:00",
  "chat_id": "d3641f32-72b7-4f7b-a87c-410f150a5040",
  "chat_ts": "2023-05-19T16:45:09.111979+00:00",
  "type": "statement",
  "id": "16437a4d-5e4b-4a36-a795-7cc5793e83b1",
  "human_input_id": "4f04f888-ab7b-4bcb-a7a0-be285a4d237c",
  "statement": "The Earth revolves around the Sun, takes about 365.25 days for a full orbit, has a slightly tilted axis, and is the third planet from the Sun.",
  "extra": "some-extra-id"
}
```

Assertions response:

```json
{
  "ts": "2023-05-19T16:46:30.208511+00:00",
  "chat_id": "d3641f32-72b7-4f7b-a87c-410f150a5040",
  "chat_ts": "2023-05-19T16:45:09.111979+00:00",
  "type": "assertions",
  "ids": [
    "db574a7a-dc86-4acf-9ae8-b590757c501b",
    "1cdf350d-11f8-4caf-a622-292096b079d7",
    "cdfba927-209e-4d41-9593-863b30c6d650",
    "33663d5c-0916-44ce-872a-eedca7849244"
  ],
  "statement_id": "16437a4d-5e4b-4a36-a795-7cc5793e83b1",
  "assertions": [
    "The Earth revolves around the Sun.",
    "The Earth takes 365.25 days to fully orbit the sun.",
    "The Earth has a slightly tilted axis.",
    "The Earth is the third planet from the Sun."
  ]
}
```

Evidence responses, one per assertion:

```json
{
  "ts": "2023-05-19T16:46:41.624677+00:00",
  "chat_id": "d3641f32-72b7-4f7b-a87c-410f150a5040",
  "chat_ts": "2023-05-19T16:45:09.111979+00:00",
  "type": "evidence",
  "id": "01781672-c169-4739-9cbe-d288de805aff",
  "assertion_id": "33663d5c-0916-44ce-872a-eedca7849244",
  "evidence": {
    "Evidence 1": {
      "ID": "https://openalex.org/W2119541020",
      "Score": "high",
      "Verdict": "contradict",
      "Explanation": "The scientific literature discusses the formation of terrestrial planets, but does not provide evidence for or against the specific assertion about the Earth's position in the solar system."
    },
    "Evidence 2": {
      "ID": "https://openalex.org/W2079958881",
      "Score": "high",
      "Verdict": "contradict",
      "Explanation": "The scientific literature discusses the formation of Mars and the terrestrial planets, but does not provide evidence for or against the specific assertion about the Earth's position in the solar system."
    },
    "Evidence 3": {
      "ID": "https://openalex.org/W2088458301",
      "Score": "high",
      "Verdict": "support",
      "Explanation": "The scientific literature discusses the detection of two Saturn-size planets that transit a Sun-like star, but does not provide evidence for or against the specific assertion about the Earth's position in the solar system."
    },
    "Summary": "Two pieces of evidence contradict the assertion, while one piece of evidence supports it.",
    "Final Verdict": "Not substantiated"
  }
}
```

It is also possible to send custom assertion to generate an evidence for:

```shell
{
  "action": "custom_assertion",
  "x-jwt-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbm9ueW1vdXMiLCJleHAiOjE2ODY5MzM4OTd9.bng3ao51Ggx-Scs8VVDFr6PBtmChYYgYTfMO_mqWw48",
  "body": "{\"chat_id\":\"d3641f32-72b7-4f7b-a87c-410f150a5040\", \"chat_ts\": \"2023-05-19T16:45:09.111979+00:00\", \"ts\": \"2023-05-17T13:51:00.703323Z\", \"assertion\":\"The Earth takes 365.25 days to fully orbit the sun.\", \"extra\":\"some-extra-id\"}"
}

```

In the above message `body` is a serialized JSON of the following structure:

```json
{
  "chat_id": "d3641f32-72b7-4f7b-a87c-410f150a5040",
  "chat_ts": "2023-05-19T16:45:09.111979+00:00",
  "ts": "2023-05-17T13:51:00.703323Z",
  "assertion": "The Earth takes 365.25 days to fully orbit the sun.",
  "extra": "some-extra-id"
}

```

Evidence response will arrive with a similar structure as for a `human_input`, with an additional field of `extra`,
which is copied from the request. 
