# Notes Backend (Flask)

Ocean Professional themed, minimal REST API for managing notes.

- Framework: Flask with flask-smorest (OpenAPI docs) and CORS
- Port: 3001
- Base URL: http://localhost:3001
- Docs: http://localhost:3001/docs

## Endpoints

- GET /notes
  - 200 OK: List all notes
- GET /notes/<id>
  - 200 OK: Returns a single note
  - 404 Not Found
- POST /notes
  - 201 Created: Creates a new note
  - 400 Bad Request: Validation error
- PUT /notes/<id>
  - 200 OK: Updates an existing note
  - 400 Bad Request: Validation error
  - 404 Not Found
- DELETE /notes/<id>
  - 204 No Content
  - 404 Not Found
- GET /
  - 200 OK: Health check

## Data model (JSON)

```json
{
  "id": "uuid",
  "title": "string (1..200)",
  "content": "string",
  "created_at": 1732131200.0,
  "updated_at": 1732131200.0
}
```

## Run locally

The API runs on port 3001. From the container root:

```bash
python run.py
```

Swagger UI available at http://localhost:3001/docs

## Example curl

List notes:
```bash
curl -s http://localhost:3001/notes | jq
```

Create a note:
```bash
curl -s -X POST http://localhost:3001/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"First note","content":"Hello"}' | jq
```

Get by id:
```bash
NOTE_ID="<copy-from-create-response>"
curl -s http://localhost:3001/notes/$NOTE_ID | jq
```

Update:
```bash
curl -s -X PUT http://localhost:3001/notes/$NOTE_ID \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated title"}' | jq
```

Delete:
```bash
curl -i -X DELETE http://localhost:3001/notes/$NOTE_ID
```

## Persistence

- Uses a lightweight JSON file store at notes_backend/app/../storage/notes.json.
- You can override the path via environment variable `NOTES_STORAGE_FILE`.

## Error responses

```json
{
  "message": "Human readable error message"
}
```

HTTP status codes are chosen appropriately (400, 404, 500, etc.).

