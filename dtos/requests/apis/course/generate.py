from pydantic import BaseModel


class GenerateCourseRequestDTO(BaseModel):

    reference_number: str
    brief: str
    target_audience: str
    course_duration_weeks: int