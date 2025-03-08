from pydantic import BaseModel


class GenerateCourseRequestDTO(BaseModel):

    reference_number: str
    sender_urn: str
    receiver_urn: str