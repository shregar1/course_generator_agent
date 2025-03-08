from fastapi import APIRouter
from http import HTTPMethod

from constants.api_lk import APILK

from controllers.apis.course.generate import GenerateCourseController

from start_utils import logger

router = APIRouter(prefix="")

# Candidate
logger.debug(f"Registering {GenerateCourseController.__name__} route.")
router.add_api_route(
    path="/course/generate",
    endpoint=GenerateCourseController().post,
    methods=[HTTPMethod.POST.value],
    name=APILK.GENERATE_COURSE
)
logger.debug(f"Registered {GenerateCourseController.__name__} route.")
