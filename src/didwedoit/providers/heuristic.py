from __future__ import annotations

import re
from collections import Counter

from ..ingest import Transcript, Turn
from ..models import ActionItem, Blocker, Confidence, Decision, MeetingRecord, Question

QUESTION_RE = re.compile(
    r"\?|^\s*(what|why|how|when|where|who)\b|\b(can you|could you|do we|should we|is there|are there|"
    r"i have (?:a |one )?(?:quick )?question|whether we)\b",
    re.I,
)
ACTION_RE = re.compile(r"\b(i will|i'll|we will|we'll|we should|we need to|we have to|you should|can you|could you|please|follow up|action item)\b", re.I)
EXPLICIT_OWNER_RE = re.compile(r"\b(i will|i'll)\b", re.I)
TASK_RE = re.compile(
    r"\b(check|investigate|compare|produce|create|make|plot|rerun|run|submit|update|add|calculate|normalize|"
    r"implement|process|train|validate|test|study|follow up|look at|take a look|double check|figure out|dig)\b",
    re.I,
)
DECISION_RE = re.compile(r"\b(we decided|we agreed|it was decided|the decision is|let's)\b", re.I)
BLOCKER_RE = re.compile(r"\b(blocked|blocking|cannot|can't|unable to|waiting for|depends on|dependency|not available)\b", re.I)
COMPLETION_RE = re.compile(r"\b(done|completed|finished|already submitted|already produced)\b", re.I)
LOGISTICS_RE = re.compile(
    r"\b(can you hear|can you see|show (the |your )?(slide|plot)|go back|full screen|stop share|start the meeting|"
    r"floor is yours|joining|connected|disconnect|wait for|agenda|continue|move on|march|be right back|"
    r"present|presentation|slides?|page|take into account|keep (that|those|this) in mind)\b",
    re.I,
)
WORDS_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")
STOPWORDS = {
    "the", "and", "that", "this", "with", "have", "from", "for", "but", "you", "are", "was", "were",
    "will", "would", "should", "could", "just", "like", "think", "maybe", "then", "there", "here", "about",
    "into", "they", "them", "their", "what", "when", "where", "which", "also", "some", "more", "very", "really",
    "okay", "yeah", "right", "today", "going", "look", "looking", "want", "need", "because", "after", "before",
}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip(" -–—.,…")


def _dedupe(items: list, field: str, limit: int) -> list:
    seen: set[str] = set()
    result = []
    for item in items:
        value = re.sub(r"\W+", " ", getattr(item, field).lower()).strip()
        key = " ".join(value.split()[:14])
        if key and key not in seen:
            seen.add(key)
            result.append(item)
        if len(result) >= limit:
            break
    return result


def _title(transcript: Transcript) -> str:
    for turn in transcript.turns:
        match = re.search(r"welcome to (?:today'?s |this week'?s )?(.{3,80}? meeting)\b", turn.text, re.I)
        if match:
            return _clean(match.group(1)).title()
    return transcript.path.stem.replace("_", " ")


def _topics(transcript: Transcript) -> list[str]:
    counts: Counter[str] = Counter()
    for turn in transcript.turns:
        for word in WORDS_RE.findall(turn.text.lower()):
            if word not in STOPWORDS and not word.isdigit():
                counts[word] += 1
    return [word for word, count in counts.most_common(8) if count >= 4]


class HeuristicProvider:
    """Conservative offline extractor.

    It is intentionally biased toward review. It provides a useful and testable
    framework without pretending that regular expressions understand a meeting.
    """

    name = "heuristic-v1"

    def analyze(self, transcript: Transcript, series: str) -> MeetingRecord:
        questions: list[Question] = []
        actions: list[ActionItem] = []
        decisions: list[Decision] = []
        blockers: list[Blocker] = []

        for index, turn in enumerate(transcript.turns):
            text = _clean(turn.text)
            if len(text) < 12 or LOGISTICS_RE.search(text):
                continue
            evidence = [turn.evidence()]
            if QUESTION_RE.search(text):
                answer = None
                for following in transcript.turns[index + 1:index + 4]:
                    if following.speaker != turn.speaker and len(following.text) >= 20 and not QUESTION_RE.search(following.text):
                        answer = _clean(following.text)
                        break
                questions.append(Question(
                    text=text,
                    status="unknown" if answer is None else "partially_answered",
                    answer=answer,
                    evidence=evidence,
                    confidence=Confidence.MEDIUM if "?" in text else Confidence.LOW,
                    needs_review=True,
                    review_reason="Confirm that this is a substantive question and whether the nearby response answers it.",
                ))
            if ACTION_RE.search(text) and TASK_RE.search(text):
                owner = turn.speaker if EXPLICIT_OWNER_RE.search(text) else None
                completed = bool(COMPLETION_RE.search(text))
                actions.append(ActionItem(
                    description=text,
                    owner=owner,
                    status="completed" if completed else "open",
                    evidence=evidence,
                    confidence=Confidence.MEDIUM if owner else Confidence.LOW,
                    needs_review=True,
                    review_reason=(
                        "Confirm that this is a real commitment and that the speaker owns it."
                        if owner else
                        "The transcript suggests work but does not establish one accountable owner."
                    ),
                ))
            if DECISION_RE.search(text):
                decisions.append(Decision(
                    description=text,
                    evidence=evidence,
                    confidence=Confidence.MEDIUM,
                    needs_review=True,
                    review_reason="Confirm that this was an actual decision rather than a suggestion.",
                ))
            if BLOCKER_RE.search(text):
                blockers.append(Blocker(
                    description=text,
                    evidence=evidence,
                    confidence=Confidence.LOW,
                    needs_review=True,
                    review_reason="Confirm that this describes a current blocker rather than a hypothetical limitation.",
                ))

        questions = _dedupe(questions, "text", 30)
        actions = _dedupe(actions, "description", 30)
        decisions = _dedupe(decisions, "description", 20)
        blockers = _dedupe(blockers, "description", 20)
        participants = list(dict.fromkeys(turn.speaker for turn in transcript.turns))
        topics = _topics(transcript)
        summary = (
            f"{len(participants)} participants discussed "
            f"{', '.join(topics[:5]) if topics else 'the recorded agenda'}. "
            f"The conservative extractor found {len(actions)} possible actions, "
            f"{len(questions)} possible questions, {len(decisions)} possible decisions, "
            f"and {len(blockers)} possible blockers. Review-marked items require human confirmation."
        )
        meeting_id = f"M-{transcript.meeting_date.strftime('%Y%m%d')}-{transcript.source.checksum_sha256[:6]}"
        return MeetingRecord(
            id=meeting_id,
            series=series,
            title=_title(transcript),
            date=transcript.meeting_date,
            participants=participants,
            executive_summary=summary,
            topics=topics,
            questions=questions,
            actions=actions,
            decisions=decisions,
            blockers=blockers,
            source=transcript.source,
            extractor=self.name,
        )
