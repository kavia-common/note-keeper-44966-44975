from marshmallow import Schema, fields, validate


class NoteSchema(Schema):
    id = fields.Str(required=True, metadata={"description": "Unique identifier for the note"})
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200), metadata={"description": "Title of the note"})
    content = fields.Str(required=True, validate=validate.Length(min=0), metadata={"description": "Content of the note"})
    created_at = fields.Float(required=True, metadata={"description": "Creation timestamp (epoch seconds)"})
    updated_at = fields.Float(required=True, metadata={"description": "Last update timestamp (epoch seconds)"})


class NoteCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200), metadata={"description": "Title of the note"})
    content = fields.Str(required=True, validate=validate.Length(min=0), metadata={"description": "Content of the note"})


class NoteUpdateSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=1, max=200), metadata={"description": "Updated title"})
    content = fields.Str(required=False, validate=validate.Length(min=0), metadata={"description": "Updated content"})
