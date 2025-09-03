from marshmallow import Schema, fields, validate, ValidationError
# from email_validator import validate_email, EmailNotValidError

class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    name = fields.Str(validate=validate.Length(max=100))
    birth_date = fields.Date()

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class MenstrualCycleSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date()
    period_length = fields.Int(validate=validate.Range(min=1))

class DailyLogSchema(Schema):
    cycle_id = fields.UUID(required=True)
    log_date = fields.Date(required=True)
    selections = fields.Dict()

class ActivityLogSchema(Schema):
    activity_type = fields.Str()
    duration_min = fields.Int(validate=validate.Range(min=1))
    exercise_rpe = fields.Int(validate=validate.Range(min=1, max=10))
    notes = fields.Str()

class CommunitySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str()

def validate_json_data(schema_class, data):
    """Validate JSON data against schema"""
    schema = schema_class()
    try:
        return schema.load(data)
    except ValidationError as e:
        raise ValidationError(f"Validation error: {e.messages}")
