import enum


class QuestionType(str, enum.Enum):
    text = "text"
    textarea = "textarea"
    single_choice = "single_choice"
    multiple_choice = "multiple_choice"
    boolean = "boolean"
    number = "number"
    slider = "slider"
    datetime = "datetime"
    rating_scale = "rating_scale"


class ReportAudience(str, enum.Enum):
    client = "client"
    career_guidance_specialist = "career_guidance_specialist"


class ProfileFieldType(str, enum.Enum):
    text = "text"
    number = "number"
    date = "date"
    datetime = "datetime"
    email = "email"
    phone = "phone"
