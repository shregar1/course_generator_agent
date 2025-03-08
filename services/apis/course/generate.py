import json

from http import HTTPStatus
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END

from abstractions.service import IService

from constants.api_status import APIStatus

from dtos.responses.base import BaseResponseDTO
from dtos.services.apis.course.generate import CourseState, ResearchOutput, CourseStructure, FullCourse

from errors.bad_input_error import BadInputError

from start_utils import llm

from utilities.dictionary import DictionaryUtility


class GenerateCourseService(IService):

    def __init__(
        self, urn: str = None, api_name: str = None
    ) -> None:
        super().__init__(urn, api_name)
        self.urn = urn
        
        self.api_name = api_name
        self.dictionary_utility = DictionaryUtility(urn=self.urn)
        self.llm = llm

    def researcher_node(self, state: CourseState) -> CourseState:
        prompt = PromptTemplate(
            input_variables=["brief", "audience", "duration"],
            template="""
            Research the topic: '{brief}' for {audience}. 
            Find credible sources and key concepts to cover in a {duration} course.
            Provide a summary of findings and list at least 5 references.
            """
        )
        research_prompt = prompt.format(brief=state["brief"], audience=state["audience"], duration=state["duration"])
        structured_llm = llm.with_structured_output(ResearchOutput)
        response = structured_llm.invoke(research_prompt)
        research_data = response.dict()
        self.logger.debug(f"Researcher Output: {json.dumps(research_data, indent=2)}")
        state["research_data"] = research_data
        return state
    
    def organizer_node(self, state: CourseState) -> CourseState:
        prompt = PromptTemplate(
            input_variables=["research_data", "audience", "duration"],
            template="""
            Based on this research: '{research_data}',
            Create a course structure with 5-6 modules for a {duration} course aimed at {audience}.
            Each module should have 2-3 lesson titles listed under a 'lessons' key.
            """
        )
        organize_prompt = prompt.format(
            research_data=json.dumps(state["research_data"]),
            audience=state["audience"],
            duration=state["duration"]
        )
        structured_llm = self.llm.with_structured_output(CourseStructure)
        response = structured_llm.invoke(organize_prompt)
        course_structure = response.dict()
        self.logger.debug(f"Organizer Output {json.dumps(course_structure, indent=2)}")
        state["course_structure"] = course_structure
        return state
    
    def writer_node(self, state: CourseState) -> CourseState:
        prompt = PromptTemplate(
            input_variables=["course_structure", "research_data", "audience"],
            template="""
            Using this course structure: '{course_structure}' and research: '{research_data}',
            Write detailed content for each lesson (at least 200 words per lesson).
            Ensure the content is beginner-friendly for {audience}.
            """
        )
        write_prompt = prompt.format(
            course_structure=json.dumps(state["course_structure"]),
            research_data=json.dumps(state["research_data"]),
            audience=state["audience"]
        )
        structured_llm = self.llm.with_structured_output(FullCourse)
        response = structured_llm.invoke(write_prompt)
        full_course = response.dict()
        self.logger.debug(f"Writer Output: {json.dumps(full_course, indent=2)}")
        state["full_course"] = full_course
        return state

    def reviewer_node(self, state: CourseState) -> CourseState:
        prompt = PromptTemplate(
            input_variables=["full_course"],
            template="""
            Review this course: '{full_course}'.
            Check for accuracy, clarity, and completeness. Suggest improvements if needed.
            """
        )
        review_prompt = prompt.format(full_course=json.dumps(state["full_course"]))
        structured_llm = llm.with_structured_output(FullCourse)
        response = structured_llm.invoke(review_prompt)
        final_course = response.dict()
        self.logger.debug(f"Reviewer Output: {json.dumps(final_course, indent=2)}")
        final_course["references"] = state["research_data"]["references"] + ["OpenAI Research Simulation 1", "OpenAI Research Simulation 2"]
        state["final_course"] = final_course
        return state

    async def run(self, data: dict) -> dict:

        self.workflow = StateGraph(CourseState)
        self.workflow.add_node("researcher", self.researcher_node)
        self.workflow.add_node("organizer", self.organizer_node)
        self.workflow.add_node("writer", self.writer_node)
        self.workflow.add_node("reviewer", self.reviewer_node)
        self.workflow.add_edge("researcher", "organizer")
        self.workflow.add_edge("organizer", "writer")
        self.workflow.add_edge("writer", "reviewer")
        self.workflow.add_edge("reviewer", END)
        self.workflow.set_entry_point("researcher")
        app = self.workflow.compile()

        brief: str = data.get("brief")
        if not brief:
            raise BadInputError(
                responseMessage="Invalid brief",
                responseKey="error_invalid_brief",
                http_status_code=HTTPStatus.BAD_REQUEST
            )

        target_audience: str = data.get("target_audience")
        if not target_audience:
            raise BadInputError(
                responseMessage="Invalid target audience",
                responseKey="error_invalid_target_audience",
                http_status_code=HTTPStatus.BAD_REQUEST
            )

        course_duration_weeks: int = data.get("course_duration_weeks")
        if not course_duration_weeks:
            raise BadInputError(
                responseMessage="Invalid course duration weeks",
                responseKey="error_invalid_course_duration_weeks",
                http_status_code=HTTPStatus.BAD_REQUEST
            )

        initial_state = {
            "brief": brief,
            "audience": target_audience,
            "duration": f"{course_duration_weeks} weeks",
            "research_data": {},
            "course_structure": {},
            "full_course": {},
            "final_course": {}
        }
        result = app.invoke(initial_state)
        response_payload = result["final_course"]

        return BaseResponseDTO(
            transactionUrn=self.urn,
            status=APIStatus.SUCCESS,
            responseMessage="Successfully generated course.",
            responseKey="success_generate_course",
            data=self.dictionary_utility.convert_dict_keys_to_camel_case(response_payload)
        )
