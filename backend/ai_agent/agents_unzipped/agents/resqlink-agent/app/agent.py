"""LangGraph agent. Exposes READ-ONLY tools; verification flags are never LLM inputs."""
import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app import tools as t

load_dotenv()


@tool
def search_people(name: str):
    """Search all person records (missing, rescued, found) by name. Partial names work."""
    return t.search_person_records(name)


@tool
def search_rescue(name: str = ""):
    """List rescued/found people, optionally filtered by name. Use name='Unknown' for unidentified people."""
    return t.search_rescue_records(name)


@tool
def get_records_for_person_id(person_id: int):
    """Cross-record view: person record plus hospital and shelter records for one person id."""
    return t.get_case_records(person_id)


@tool
def search_hospitals_by_name(name: str):
    """Search hospital records by name."""
    return t.search_hospital_records_by_name(name)


@tool
def search_shelters_by_name(name: str):
    """Search shelter records by name."""
    return t.search_shelter_records_by_name(name)


@tool
def find_matches(missing_person_id: int):
    """Find and score possible rescued/found matches for a MISSING person id.
    Results already include each candidate's hospital and shelter records."""
    return t.find_possible_matches(missing_person_id)


@tool
def check_firewall(missing_person_id: int, candidate_id: int):
    """Run the Reunification Firewall for a (missing person, candidate) pair.
    Verification flags are read from the case record, which only authorized humans can change."""
    return t.run_firewall_for_case(missing_person_id, candidate_id)


SYSTEM_PROMPT = """You are ResQLink AI, an emergency disaster reunification assistant for authorized responders.

Workflow when asked about a missing person:
1. search_people to find the missing person's record and id.
2. find_matches with that id. It returns scored candidates with hospital and shelter records.
3. For the best candidate(s), call check_firewall.
4. Summarise: candidate id, score, matching reasons, any conflicts, hospital/shelter trail, firewall decision.

Rules:
- You cannot verify identity or family relationships and you cannot mark anyone reunited.
  Those steps are done only by authorized human officers through a separate system.
- An AI match is a lead, never a confirmation. Never tell a family that someone has been found.
- Only report facts that appear in tool results. Never invent locations, times or medical conditions.
- If nothing matches, say so plainly.
- Be concise."""


@lru_cache(maxsize=1)
def get_agent():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        temperature=0,
    )
    return create_react_agent(
        model=llm,
        tools=[
            search_people,
            search_rescue,
            get_records_for_person_id,
            search_hospitals_by_name,
            search_shelters_by_name,
            find_matches,
            check_firewall,
        ],
        prompt=SYSTEM_PROMPT,
    )


def run_agent(message: str) -> str:
    result = get_agent().invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content
