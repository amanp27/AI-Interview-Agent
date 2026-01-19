import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("interview-tools")


class InterviewTools:
    """Tools and utilities for the interview assistant"""
    
    def __init__(self):
        self.candidate_notes = []
        self.interview_stage = "introduction"
        self.questions_asked = []
        self.start_time = datetime.now()
        self.candidate_info = {}
    
    def record_note(self, note: str, category: str = "general") -> dict:
        """
        Record an important note or observation about the candidate
        
        Args:
            note: The note to record
            category: Category (technical, behavioral, experience, communication, general)
        
        Returns:
            Dictionary with note details
        """
        note_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "note": note,
            "stage": self.interview_stage
        }
        self.candidate_notes.append(note_entry)
        logger.info(f"Recorded note [{category}]: {note}")
        
        return note_entry
    
    def update_interview_stage(self, stage: str) -> str:
        """
        Update the current stage of the interview
        
        Args:
            stage: New stage (introduction, technical, behavioral, experience, questions, closing)
        
        Returns:
            Confirmation message
        """
        old_stage = self.interview_stage
        self.interview_stage = stage
        logger.info(f"Interview stage: {old_stage} -> {stage}")
        
        return f"Stage updated to {stage}"
    
    def mark_question_asked(self, question: str, category: Optional[str] = None) -> None:
        """
        Track questions that have been asked to avoid repetition
        
        Args:
            question: The question that was asked
            category: Optional category of the question
        """
        self.questions_asked.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "stage": self.interview_stage,
            "category": category
        })
        logger.info(f"Question logged: {question}")
    
    def store_candidate_info(self, key: str, value: str) -> None:
        """
        Store important information about the candidate
        
        Args:
            key: Information key (e.g., 'name', 'current_role', 'experience_years')
            value: Information value
        """
        self.candidate_info[key] = value
        logger.info(f"Stored candidate info - {key}: {value}")
    
    def get_notes_summary(self) -> str:
        """Get a formatted summary of all notes"""
        if not self.candidate_notes:
            return "No notes recorded yet."
        
        summary = f"Interview Notes Summary ({len(self.candidate_notes)} total)\n"
        summary += "=" * 50 + "\n\n"
        
        # Group by category
        categories = {}
        for note in self.candidate_notes:
            cat = note["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(note)
        
        # Format by category
        for category, notes in categories.items():
            summary += f"{category.upper()} ({len(notes)}):\n"
            for note in notes:
                summary += f"  • {note['note']} [{note['stage']}]\n"
            summary += "\n"
        
        return summary
    
    def get_asked_questions(self) -> list:
        """Get list of questions that have been asked"""
        return [q["question"] for q in self.questions_asked]
    
    def get_interview_duration(self) -> str:
        """Get the current duration of the interview"""
        duration = datetime.now() - self.start_time
        minutes = int(duration.total_seconds() / 60)
        seconds = int(duration.total_seconds() % 60)
        return f"{minutes}m {seconds}s"
    
    def get_interview_summary(self) -> dict:
        """Get a complete summary of the interview session"""
        return {
            "duration": self.get_interview_duration(),
            "current_stage": self.interview_stage,
            "total_notes": len(self.candidate_notes),
            "questions_asked": len(self.questions_asked),
            "candidate_info": self.candidate_info,
            "notes_by_category": self._get_notes_by_category()
        }
    
    def _get_notes_by_category(self) -> dict:
        """Helper to group notes by category"""
        categories = {}
        for note in self.candidate_notes:
            cat = note["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(note["note"])
        return categories
    
    def export_interview_data(self) -> dict:
        """Export all interview data for storage/analysis"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration": self.get_interview_duration(),
            "final_stage": self.interview_stage,
            "candidate_info": self.candidate_info,
            "notes": self.candidate_notes,
            "questions_asked": self.questions_asked,
            "summary": self.get_interview_summary()
        }


# Scoring/Rating system (optional - for future use)
class InterviewScoring:
    """Interview scoring and evaluation system"""
    
    CRITERIA = {
        "technical_skills": {"weight": 0.30, "max_score": 10},
        "communication": {"weight": 0.20, "max_score": 10},
        "problem_solving": {"weight": 0.25, "max_score": 10},
        "experience": {"weight": 0.15, "max_score": 10},
        "cultural_fit": {"weight": 0.10, "max_score": 10},
    }
    
    def __init__(self):
        self.scores = {criterion: 0 for criterion in self.CRITERIA.keys()}
        self.feedback = {criterion: "" for criterion in self.CRITERIA.keys()}
    
    def set_score(self, criterion: str, score: int, feedback: str = "") -> None:
        """Set score for a specific criterion"""
        if criterion in self.CRITERIA:
            max_score = self.CRITERIA[criterion]["max_score"]
            self.scores[criterion] = min(score, max_score)
            if feedback:
                self.feedback[criterion] = feedback
            logger.info(f"Score set - {criterion}: {score}/{max_score}")
    
    def calculate_weighted_score(self) -> float:
        """Calculate the overall weighted score"""
        total = 0
        for criterion, score in self.scores.items():
            weight = self.CRITERIA[criterion]["weight"]
            max_score = self.CRITERIA[criterion]["max_score"]
            normalized_score = (score / max_score) * 100
            total += normalized_score * weight
        return round(total, 2)
    
    def get_evaluation_report(self) -> dict:
        """Get complete evaluation report"""
        return {
            "individual_scores": self.scores,
            "weighted_score": self.calculate_weighted_score(),
            "feedback": self.feedback,
            "criteria_weights": {k: v["weight"] for k, v in self.CRITERIA.items()}
        }