# Local AI / debug integration API

The desktop app can expose your saved HE75 profiles to a helper running on the **same PC**. It is designed for a local AI assistant or debugging tool, not for remote control.

## Enable it

1. Open `python app.py`.
2. In **Local AI / debug integration**, enable **Local API**.
3. Copy the displayed token with **Copy token**. The endpoint is shown beside the switch.

The service binds only to `127.0.0.1`; no LAN address, cloud connection, shell command, arbitrary HID packet, or macro endpoint exists. It is off every time the app starts. The token is stored locally in `%LOCALAPPDATA%\HE75 Toolkit\local-api.json`, is never returned by the API or logged, and can be replaced with **Regenerate token**.

Every request needs `Authorization: Bearer <your-token>`.

```powershell
$token = '<paste the copied token here>'
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod http://127.0.0.1:PORT/v1/status -Headers $headers
Invoke-RestMethod http://127.0.0.1:PORT/v1/profiles -Headers $headers
Invoke-RestMethod http://127.0.0.1:PORT/v1/profiles/valorant -Headers $headers
```

## Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/v1/status` | Current toolkit state; does not query or write the keyboard. |
| `GET` | `/v1/profiles` | Saved profile library. |
| `GET` | `/v1/profiles/{id}` | One saved profile. |
| `GET` | `/v1/logs` | In-memory integration events when available. |
| `POST` | `/v1/preview` | Read-only plan for one saved profile. |
| `POST` | `/v1/apply/{id}` | Apply and verify a saved profile. Requires explicit confirmation. |

Preview is read-only:

```powershell
Invoke-RestMethod http://127.0.0.1:PORT/v1/preview -Method Post -Headers $headers -ContentType 'application/json' -Body '{"profile_id":"valorant"}'
```

Applying a profile writes the same verified Hall/lighting operations the desktop app uses. The request body must be exactly `{"confirm":true}`; omission, `false`, or extra fields is rejected.

```powershell
Invoke-RestMethod http://127.0.0.1:PORT/v1/apply/valorant -Method Post -Headers $headers -ContentType 'application/json' -Body '{"confirm":true}'
```

Keep the token private. Regenerate it if you paste it somewhere you do not trust.
