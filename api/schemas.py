from marshmallow import validate, validates, validates_schema, ValidationError, post_dump, post_load, fields
from api import ma, db
from api.auth import token_auth
from api.models import User, Token, Meal, Food, Unit

paginated_schema_cache = {}

class EmptySchema(ma.Schema):
    pass

class DateTimePaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.DateTime(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')

class StringPaginationSchema(ma.Schema):
    class Meta:
        ordered = True

    limit = ma.Integer()
    offset = ma.Integer()
    after = ma.String(load_only=True)
    count = ma.Integer(dump_only=True)
    total = ma.Integer(dump_only=True)

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('offset') is not None and data.get('after') is not None:
            raise ValidationError('Cannot specify both offset and after')

def PaginatedCollection(schema, pagination_schema=StringPaginationSchema):
    if schema in paginated_schema_cache:
        return paginated_schema_cache[schema]

    class PaginatedSchema(ma.Schema):
        class Meta:
            ordered = True

        pagination = ma.Nested(pagination_schema)
        data = ma.Nested(schema, many=True)

    PaginatedSchema.__name__ = 'Paginated{}'.format(schema.__class__.__name__)
    paginated_schema_cache[schema] = PaginatedSchema
    return PaginatedSchema

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(required=True, validate=validate.Length(min=3, max=64))
    email = ma.auto_field(required=True, validate=[validate.Length(max=120), validate.Email()])
    password = ma.String(required=True, load_only=True, validate=validate.Length(min=3))
    first_active = ma.auto_field(dump_only=True)
    last_active = ma.auto_field(dump_only=True)
    meals = ma.Dict(dump_only=True)

    @validates('username')
    def validate_username(self, value):
        if not value[0].isalpha():
            raise ValidationError('Username must start with a letter')
        user = token_auth.current_user()
        old_username = user.username if user else None
        if value != old_username and db.session.scalar(User.select().filter_by(username=value)):
            raise ValidationError('Use a different username.')

    @validates('email')
    def validate_email(self, value):
        user = token_auth.current_user()
        old_email = user.email if user else None
        if value != old_email and db.session.scalar(User.select().filter_by(email=value)):
            raise ValidationError('Use a different email.')

    @post_dump
    def fix_datetimes(self, data, **kwargs):
        data['first_active'] += 'Z'
        data['last_active'] += 'Z'
        return data

class TokenSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Token
        ordered = True

    id = ma.auto_field(dump_only=True)
    access_token = ma.auto_field(required=True)
    access_expiration = ma.auto_field(dump_only=True)
    refresh_token = ma.auto_field()
    refresh_expiration = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(dump_only=True)

class MealSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Meal
        ordered = True

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True)
    last_used = ma.auto_field(dump_only=True)
    use_count = ma.auto_field(dump_only=True)
    is_vegan = ma.auto_field()

class NutritionSchema(ma.Schema):
    calories = fields.Integer(required=False, allow_none=True)
    protein = fields.Integer(required=False, allow_none=True)
    carbs = fields.Integer(required=False, allow_none=True)
    fats = fields.Integer(required=False, allow_none=True)

    @post_load
    def make_nutrition(self, data, **kwargs):
        return data

class FoodSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Food
        ordered = True

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True)
    nutrition = ma.Nested(NutritionSchema)

class UnitSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Unit
        ordered = True

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True)
    abbreviation = ma.auto_field(required=True)

class PasswordResetRequestSchema(ma.Schema):
    class Meta:
        ordered = True

    email = ma.String(required=True, validate=[validate.Length(max=120), validate.Email()])

class PasswordResetSchema(ma.Schema):
    class Meta:
        ordered = True

    token = ma.String(required=True)
    new_password = ma.String(required=True, validate=validate.Length(min=3))

class OAuth2Schema(ma.Schema):
    code = ma.String(required=True)
    state = ma.String(required=True)