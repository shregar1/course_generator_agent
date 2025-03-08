from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, TypedDict, Dict


class CourseState(TypedDict):
    brief: str
    audience: str
    duration: str
    research_data: Dict
    course_structure: Dict
    full_course: Dict
    final_course: Dict


class ResearchOutput(BaseModel):
    summary: str = Field(description="Summary of research findings")
    references: List[str] = Field(description="List of at least 5 references")


class Module(BaseModel):
    title: str = Field(description="Title of the module")
    lessons: List[str] = Field(description="List of 2-3 lesson titles for this module")


class CourseStructure(BaseModel):
    course_title: str = Field(description="Title of the course")
    description: str = Field(description="Brief description of the course")
    modules: List[Module] = Field(description="List of 5-6 modules, each with lesson titles")


class LessonContent(BaseModel):
    title: str = Field(description="Title of the lesson")
    content: str = Field(description="Detailed content for the lesson, at least 200 words")


class FullModule(BaseModel):
    title: str = Field(description="Title of the module")
    lessons: List[LessonContent] = Field(description="List of lessons with detailed content")


class FullCourse(BaseModel):
    course_title: str = Field(description="Title of the course")
    description: str = Field(description="Brief description of the course")
    modules: List[FullModule] = Field(description="List of modules with detailed lessons")