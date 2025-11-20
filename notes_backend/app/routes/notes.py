from flask.views import MethodView
from flask_smorest import Blueprint, abort

from ..models import get_repository, PersistenceError
from ..schemas import NoteSchema, NoteCreateSchema, NoteUpdateSchema

blp = Blueprint(
    "Notes",
    "notes",
    url_prefix="/notes",
    description="CRUD operations for notes",
)


@blp.route("/")
class NotesList(MethodView):
    @blp.response(200, NoteSchema(many=True), description="List all notes")
    def get(self):
        """List all notes."""
        try:
            repo = get_repository()
            return repo.list_notes()
        except PersistenceError as exc:
            abort(500, message=str(exc))

    @blp.arguments(NoteCreateSchema, example={"title": "My Note", "content": "Hello world"})
    @blp.response(201, NoteSchema, description="Note created")
    def post(self, payload):
        """Create a new note."""
        try:
            repo = get_repository()
            note = repo.create_note(title=payload["title"], content=payload["content"])
            return note
        except PersistenceError as exc:
            abort(500, message=str(exc))


@blp.route("/<string:note_id>")
class NotesDetail(MethodView):
    @blp.response(200, NoteSchema, description="Get note by id")
    def get(self, note_id: str):
        """Get a note by id."""
        try:
            repo = get_repository()
            note = repo.get_note(note_id)
            if not note:
                abort(404, message="Note not found")
            return note
        except PersistenceError as exc:
            abort(500, message=str(exc))

    @blp.arguments(NoteUpdateSchema, example={"title": "Updated title"})
    @blp.response(200, NoteSchema, description="Updated note")
    def put(self, payload, note_id: str):
        """Update a note by id."""
        if not payload:
            abort(400, message="No fields to update")
        try:
            repo = get_repository()
            updated = repo.update_note(note_id, title=payload.get("title"), content=payload.get("content"))
            if not updated:
                abort(404, message="Note not found")
            return updated
        except PersistenceError as exc:
            abort(500, message=str(exc))

    @blp.response(204, description="Note deleted")
    def delete(self, note_id: str):
        """Delete a note by id."""
        try:
            repo = get_repository()
            deleted = repo.delete_note(note_id)
            if not deleted:
                abort(404, message="Note not found")
            # No content response
            return ""
        except PersistenceError as exc:
            abort(500, message=str(exc))
