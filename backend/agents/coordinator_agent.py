"""
Autonomous Research Coordinator Agent – Phase 15

Acts as the brain of the Smart Research Assistant. Given a free-form
user query it:
  1. Classifies the intent (IntentType)
  2. Builds a WorkflowPlan (ordered list of agent steps)
  3. Executes each agent in sequence, feeding results forward
  4. Returns a CoordinatorResult that the API layer can serialize

This module is intentionally standalone: it imports the existing
specialist agents via the CoordinatorAgent router but drives their
execution autonomously without any user intervention.
"""

from __future__ import annotations

import re
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy.orm import Session

from .coordinator import CoordinatorAgent
from .search_agent import SearchAgent
from ..services.paper_search_service import paper_search_service
from ..models import Paper

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  INTENT CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

class IntentType(str, Enum):
    SEARCH_PAPERS            = "search_papers"
    SUMMARIZE_PAPERS         = "summarize_papers"
    COMPARE_PAPERS           = "compare_papers"
    FIND_RESEARCH_GAPS       = "find_research_gaps"
    GENERATE_LITERATURE_REVIEW = "generate_literature_review"
    GENERAL_RAG_CHAT         = "general_rag_chat"


# Keyword patterns for rule-based intent classification
_INTENT_RULES: list[tuple[IntentType, list[str]]] = [
    (IntentType.GENERATE_LITERATURE_REVIEW, [
        "literature review", "systematic review", "survey paper",
        "write a review", "generate review", "create survey",
    ]),
    (IntentType.FIND_RESEARCH_GAPS, [
        "research gap", "gap analysis", "unexplored", "future work",
        "find gaps", "identify gaps", "research opportunity",
        "promising direction", "open problem",
    ]),
    (IntentType.COMPARE_PAPERS, [
        "compare", "comparison", "contrast", "difference between",
        "vs ", "versus", "benchmark", "evaluate against",
    ]),
    (IntentType.SUMMARIZE_PAPERS, [
        "summarize", "summary", "summarise", "key findings",
        "extract findings", "what does the paper say", "overview of",
        "main contribution",
    ]),
    (IntentType.SEARCH_PAPERS, [
        "find papers", "search for", "recent papers", "discover papers",
        "find research", "look up", "find studies", "find articles",
        "find publications", "fetch papers", "get papers",
    ]),
    (IntentType.GENERAL_RAG_CHAT, [
        "what", "how", "why", "explain", "methodology", "tell me",
        "can you", "describe", "definition",
    ]),
]


def classify_intent(query: str) -> IntentType:
    """Rule-based intent classifier. Fast, no LLM needed."""
    lower = query.lower()
    for intent, keywords in _INTENT_RULES:
        for kw in keywords:
            if kw in lower:
                return intent
    return IntentType.SEARCH_PAPERS  # safe default


# ─────────────────────────────────────────────────────────────────────────────
#  TOPIC EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_topic(query: str, intent: IntentType) -> str:
    """
    Strip intent-signalling verbs to get the bare research topic.

    Examples:
      "Find research gaps in Federated Learning Security"  → "Federated Learning Security"
      "Generate a literature review on Healthcare AI"      → "Healthcare AI"
      "Compare recent Edge AI papers"                      → "Edge AI"
    """
    lower = query.lower()

    # Strip common prefixes by pattern
    patterns = [
        r"^generate\s+(?:a\s+)?literature\s+review\s+(?:on|about|for)\s+",
        r"^(?:find|identify|discover)\s+(?:research\s+)?gaps?\s+(?:in|for|on|about)\s+",
        r"^(?:compare|contrast)\s+(?:recent\s+)?(?:papers?\s+(?:on|about|in)\s+)?",
        r"^(?:find|search\s+for|get|fetch|discover|look\s+up)\s+(?:recent\s+)?papers?\s+(?:on|about|in)\s+",
        r"^(?:summarize|summarise|generate\s+(?:a\s+)?summary\s+(?:of|for))\s+",
        r"^(?:find|search\s+for|discover)\s+(?:research|studies|articles)?\s+(?:on|about|in)\s+",
    ]
    for pat in patterns:
        match = re.match(pat, lower)
        if match:
            topic = query[match.end():].strip()
            # Strip trailing "papers", "studies", etc.
            topic = re.sub(r'\s+(papers?|studies|articles|publications?)$', '', topic, flags=re.IGNORECASE)
            if topic:
                return topic

    # Fallback: return original query trimmed to 80 chars
    return query.strip()[:80]


# ─────────────────────────────────────────────────────────────────────────────
#  WORKFLOW PLAN
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class WorkflowStep:
    step_number: int
    agent_name: str
    description: str
    status: str = "pending"   # pending | running | done | skipped | failed


@dataclass
class WorkflowPlan:
    workflow_name: str
    intent: IntentType
    topic: str
    steps: list[WorkflowStep]
    estimated_duration: str

    def to_dict(self) -> dict:
        return {
            "workflow_name": self.workflow_name,
            "intent": self.intent.value,
            "topic": self.topic,
            "estimated_duration": self.estimated_duration,
            "steps": [
                {
                    "step_number": s.step_number,
                    "agent_name": s.agent_name,
                    "description": s.description,
                    "status": s.status,
                }
                for s in self.steps
            ],
        }


_WORKFLOW_TEMPLATES: dict[IntentType, dict] = {
    IntentType.SEARCH_PAPERS: {
        "name": "Paper Discovery",
        "duration": "~5-10 seconds",
        "steps": [
            ("Search Agent", "Search OpenAlex for relevant papers"),
        ],
    },
    IntentType.SUMMARIZE_PAPERS: {
        "name": "Paper Summarization",
        "duration": "~2-3 minutes",
        "steps": [
            ("Search Agent",   "Search OpenAlex for relevant papers"),
            ("Summary Agent",  "Summarize each discovered paper"),
        ],
    },
    IntentType.COMPARE_PAPERS: {
        "name": "Comparative Analysis",
        "duration": "~3-5 minutes",
        "steps": [
            ("Search Agent",     "Search OpenAlex for relevant papers"),
            ("Summary Agent",    "Summarize each paper"),
            ("Comparison Agent", "Compare methodologies and findings"),
        ],
    },
    IntentType.FIND_RESEARCH_GAPS: {
        "name": "Research Gap Analysis",
        "duration": "~5-8 minutes",
        "steps": [
            ("Search Agent",     "Search OpenAlex for relevant papers"),
            ("Summary Agent",    "Summarize each paper"),
            ("Comparison Agent", "Compare methodologies and findings"),
            ("Gap Agent",        "Identify unexplored areas and opportunities"),
        ],
    },
    IntentType.GENERATE_LITERATURE_REVIEW: {
        "name": "Literature Review Generation",
        "duration": "~8-12 minutes",
        "steps": [
            ("Search Agent",              "Search OpenAlex for relevant papers"),
            ("Summary Agent",             "Summarize each paper"),
            ("Comparison Agent",          "Compare methodologies and findings"),
            ("Gap Agent",                 "Identify research gaps"),
            ("Literature Review Agent",   "Synthesize a comprehensive academic review"),
        ],
    },
    IntentType.GENERAL_RAG_CHAT: {
        "name": "Research Q&A",
        "duration": "~30-60 seconds",
        "steps": [
            ("Chat Agent", "Answer using available paper context"),
        ],
    },
}


def build_workflow(intent: IntentType, topic: str) -> WorkflowPlan:
    tmpl = _WORKFLOW_TEMPLATES[intent]
    steps = [
        WorkflowStep(i + 1, name, desc)
        for i, (name, desc) in enumerate(tmpl["steps"])
    ]
    return WorkflowPlan(
        workflow_name=tmpl["name"],
        intent=intent,
        topic=topic,
        steps=steps,
        estimated_duration=tmpl["duration"],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  COORDINATOR RESULT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CoordinatorResult:
    workflow: WorkflowPlan
    papers: list[dict] = field(default_factory=list)
    summaries: list[dict] = field(default_factory=list)
    comparison: str | None = None
    gap_analysis: dict | None = None
    literature_review: str | None = None
    chat_answer: str | None = None
    final_text: str = ""
    result_type: str = "text"     # text | papers | mixed
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "workflow": self.workflow.to_dict(),
            "result_type": self.result_type,
            "final_text": self.final_text,
            "papers": self.papers,
            "summaries": self.summaries,
            "comparison": self.comparison,
            "gap_analysis": self.gap_analysis,
            "literature_review": self.literature_review,
            "chat_answer": self.chat_answer,
            "error": self.error,
        }


# ─────────────────────────────────────────────────────────────────────────────
#  AUTONOMOUS COORDINATOR AGENT
# ─────────────────────────────────────────────────────────────────────────────

class AutonomousCoordinator:
    """
    Drives the full multi-agent research pipeline autonomously.

    Usage (inside a background thread):
        ac = AutonomousCoordinator(db, task_service, task_id)
        result = ac.run(query)
    """

    PAPERS_PER_SEARCH = 5  # keep summaries/comparison manageable

    def __init__(self, db: Session, task_service=None, task_id: str | None = None):
        self.db = db
        self.task_service = task_service
        self.task_id = task_id
        self.coordinator = CoordinatorAgent(db)
        self.search_agent = SearchAgent(db)

    # ── helpers ─────────────────────────────────────────────────────────────

    def _update(self, progress: int, step: str, step_status: str = "running",
                step_index: int | None = None, plan: WorkflowPlan | None = None):
        """Update task_service and optionally the workflow plan step status."""
        if self.task_service and self.task_id:
            self.task_service.update(
                self.task_id,
                progress=progress,
                current_step=step,
            )
        if plan is not None and step_index is not None:
            plan.steps[step_index].status = step_status

    def _paper_to_dict(self, p: Paper) -> dict:
        return {
            "id": p.id,
            "title": p.title,
            "authors": p.authors,
            "abstract": p.abstract,
            "year": p.year,
            "doi": p.doi,
            "source": p.source,
        }

    # ── main entry point ─────────────────────────────────────────────────────

    def run(self, query: str) -> CoordinatorResult:
        intent = classify_intent(query)
        topic  = extract_topic(query, intent)
        plan   = build_workflow(intent, topic)

        logger.info(f"[AutoCoordinator] intent={intent.value} topic='{topic}'")
        result = CoordinatorResult(workflow=plan)

        try:
            if intent == IntentType.GENERAL_RAG_CHAT:
                self._run_chat(query, result, plan)
            elif intent == IntentType.SEARCH_PAPERS:
                self._run_search(topic, result, plan)
            elif intent == IntentType.SUMMARIZE_PAPERS:
                self._run_search_and_summarize(topic, result, plan)
            elif intent == IntentType.COMPARE_PAPERS:
                self._run_search_summarize_compare(topic, result, plan)
            elif intent == IntentType.FIND_RESEARCH_GAPS:
                self._run_gap_pipeline(topic, result, plan)
            elif intent == IntentType.GENERATE_LITERATURE_REVIEW:
                self._run_review_pipeline(topic, result, plan)
        except Exception as exc:
            logger.exception(f"[AutoCoordinator] pipeline error: {exc}")
            result.error = str(exc)
            result.final_text = f"❌ Pipeline error: {exc}"

        return result

    # ── pipeline stages ──────────────────────────────────────────────────────

    def _search_papers(self, topic: str, plan: WorkflowPlan, step_idx: int) -> list[Paper]:
        step = plan.steps[step_idx]
        step.status = "running"
        self._update(10, f"Searching papers on '{topic}'…", plan=plan, step_index=step_idx)

        papers = self.search_agent.search_and_store(topic, limit=self.PAPERS_PER_SEARCH)
        step.status = "done"
        return papers

    def _summarize_papers(self, papers: list[Paper], plan: WorkflowPlan, step_idx: int,
                          base_progress: int = 30) -> list:
        step = plan.steps[step_idx]
        step.status = "running"
        summaries = []
        total = len(papers)
        for i, paper in enumerate(papers):
            pct = base_progress + int((i / max(total, 1)) * 20)
            self._update(pct, f"Summarizing paper {i+1}/{total}: {paper.title[:50]}…",
                         plan=plan, step_index=step_idx)
            try:
                s = self.coordinator.route_summary(paper.id)
                summaries.append(s)
            except Exception as e:
                logger.warning(f"Summary failed for paper {paper.id}: {e}")
        step.status = "done"
        return summaries

    def _compare_papers(self, paper_ids: list[int], topic: str,
                        plan: WorkflowPlan, step_idx: int, progress: int = 60) -> str | None:
        if len(paper_ids) < 2:
            plan.steps[step_idx].status = "skipped"
            return None
        step = plan.steps[step_idx]
        step.status = "running"
        self._update(progress, "Comparing methodologies and findings…",
                     plan=plan, step_index=step_idx)
        try:
            cmp = self.coordinator.route_comparison(paper_ids)
            step.status = "done"
            return cmp.result
        except Exception as e:
            logger.warning(f"Comparison failed: {e}")
            step.status = "failed"
            return None

    def _gap_analysis(self, topic: str, paper_ids: list[int],
                      plan: WorkflowPlan, step_idx: int, progress: int = 75) -> dict | None:
        step = plan.steps[step_idx]
        step.status = "running"
        self._update(progress, f"Identifying research gaps in '{topic}'…",
                     plan=plan, step_index=step_idx)
        try:
            gap = self.coordinator.route_gap(topic, paper_ids)
            step.status = "done"
            return {"raw_text": gap.result, "id": gap.id}
        except Exception as e:
            logger.warning(f"Gap analysis failed: {e}")
            step.status = "failed"
            return None

    def _literature_review(self, topic: str, paper_ids: list[int],
                           plan: WorkflowPlan, step_idx: int, progress: int = 88) -> str | None:
        step = plan.steps[step_idx]
        step.status = "running"
        self._update(progress, f"Writing literature review on '{topic}'…",
                     plan=plan, step_index=step_idx)
        try:
            rev = self.coordinator.route_review(topic, paper_ids)
            step.status = "done"
            return rev.result
        except Exception as e:
            logger.warning(f"Literature review failed: {e}")
            step.status = "failed"
            return None

    # ── full pipelines ────────────────────────────────────────────────────────

    def _run_chat(self, query: str, result: CoordinatorResult, plan: WorkflowPlan):
        plan.steps[0].status = "running"
        self._update(10, "Processing your question…", plan=plan, step_index=0)
        try:
            answer, _ = self.coordinator.route_chat(query)
            result.chat_answer = answer
            result.final_text = answer
            result.result_type = "text"
        except Exception as e:
            result.final_text = f"I couldn't find relevant context. Please upload papers first."
        plan.steps[0].status = "done"
        self._update(100, "Complete")

    def _run_search(self, topic: str, result: CoordinatorResult, plan: WorkflowPlan):
        papers = self._search_papers(topic, plan, 0)
        result.papers = [self._paper_to_dict(p) for p in papers]
        result.result_type = "papers"
        n = len(papers)
        result.final_text = f"Found **{n} papers** on *{topic}*. Select papers to analyze further."
        self._update(100, "Complete")

    def _run_search_and_summarize(self, topic: str, result: CoordinatorResult, plan: WorkflowPlan):
        papers = self._search_papers(topic, plan, 0)
        result.papers = [self._paper_to_dict(p) for p in papers]

        summaries = self._summarize_papers(papers, plan, 1, base_progress=25)
        result.summaries = [
            {
                "paper_id": s.paper_id,
                "objective": s.objective,
                "methodology": s.methodology,
                "findings": s.findings,
            }
            for s in summaries if s
        ]

        result.result_type = "mixed"
        result.final_text = self._format_summaries_text(result.summaries, topic)
        self._update(100, "Complete")

    def _run_search_summarize_compare(self, topic: str, result: CoordinatorResult, plan: WorkflowPlan):
        papers = self._search_papers(topic, plan, 0)
        result.papers = [self._paper_to_dict(p) for p in papers]
        paper_ids = [p.id for p in papers]

        self._summarize_papers(papers, plan, 1, base_progress=25)
        comparison = self._compare_papers(paper_ids, topic, plan, 2, progress=60)
        result.comparison = comparison

        result.result_type = "text"
        result.final_text = comparison or "Comparison could not be generated (need ≥2 papers)."
        self._update(100, "Complete")

    def _run_gap_pipeline(self, topic: str, result: CoordinatorResult, plan: WorkflowPlan):
        papers = self._search_papers(topic, plan, 0)
        result.papers = [self._paper_to_dict(p) for p in papers]
        paper_ids = [p.id for p in papers]

        self._summarize_papers(papers, plan, 1, base_progress=20)
        self._compare_papers(paper_ids, topic, plan, 2, progress=55)
        gap = self._gap_analysis(topic, paper_ids, plan, 3, progress=72)
        result.gap_analysis = gap

        result.result_type = "text"
        result.final_text = (gap or {}).get("raw_text", "Gap analysis could not be generated.")
        self._update(100, "Complete")

    def _run_review_pipeline(self, topic: str, result: CoordinatorResult, plan: WorkflowPlan):
        papers = self._search_papers(topic, plan, 0)
        result.papers = [self._paper_to_dict(p) for p in papers]
        paper_ids = [p.id for p in papers]

        self._summarize_papers(papers, plan, 1, base_progress=15)
        self._compare_papers(paper_ids, topic, plan, 2, progress=45)
        self._gap_analysis(topic, paper_ids, plan, 3, progress=65)
        review = self._literature_review(topic, paper_ids, plan, 4, progress=82)
        result.literature_review = review

        result.result_type = "text"
        result.final_text = review or "Literature review could not be generated."
        self._update(100, "Complete")

    # ── formatting helpers ────────────────────────────────────────────────────

    def _format_summaries_text(self, summaries: list[dict], topic: str) -> str:
        if not summaries:
            return f"No summaries could be generated for papers on *{topic}*."
        lines = [f"## Summaries – {topic}\n"]
        for i, s in enumerate(summaries, 1):
            lines.append(f"### Paper {i}")
            if s.get("objective"):
                lines.append(f"**Objective:** {s['objective']}\n")
            if s.get("methodology"):
                lines.append(f"**Methodology:** {s['methodology']}\n")
            if s.get("findings"):
                lines.append(f"**Findings:** {s['findings']}\n")
        return "\n".join(lines)
