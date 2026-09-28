# Debug report

## Planned debugging exercise

For `GET /messages/999999`, temporarily return the value from
`_messages.get(message_id)` without checking whether it is `None`. Place a
breakpoint on that return statement. The debugger should show that `message`
is `None` for an unknown ID.

## Traceback to capture before the fix

```text
Traceback (most recent call last):
  File "main.py", line 95, in get_message
    return storage.get(message_id)
  File "storage.py", line 53, in get
    return message.id
AttributeError: 'NoneType' object has no attribute 'id'
```

## Implemented fix

`storage.get()` now raises `MessageNotFound(message_id)` instead. The FastAPI
exception handler turns it into a `404` response with the stable error code
`message_not_found`.

## Verification note

The project virtual environment cannot currently start Python because it fails
to import the standard `encodings` module. Run the debugging exercise and
replace the example traceback above with the captured traceback once the local
Python installation or virtual environment has been repaired.
