import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import openai
import os

logger = logging.getLogger("interview-evaluation")


class InterviewEvaluator:
    """
    Evaluates completed interviews using AI analysis
    Generates comprehensive assessment, ratings, and recommendations
    """
    
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.evaluations_dir = Path("evaluations")
        self.evaluations_dir.mkdir(exist_ok=True)
    
    async def evaluate_interview(
        self,
        candidate_name: str,
        position: str,
        transcript: str,
        interview_notes: List[Dict],
        duration_minutes: int,
        candidate_info: Dict = None
    ) -> Dict:
        """
        Main evaluation function - analyzes the interview and generates comprehensive report
        
        Args:
            candidate_name: Name of the candidate
            position: Position they interviewed for
            transcript: Full interview transcript
            interview_notes: Notes taken during interview
            duration_minutes: Interview duration
            candidate_info: Additional candidate information
            
        Returns:
            Complete evaluation dictionary
        """
        
        logger.info(f"Starting evaluation for {candidate_name} - {position}")
        
        # Generate AI evaluation
        ai_assessment = await self._generate_ai_assessment(
            candidate_name=candidate_name,
            position=position,
            transcript=transcript,
            interview_notes=interview_notes,
            duration_minutes=duration_minutes
        )
        
        # Structure the complete evaluation
        evaluation = {
            "metadata": {
                "candidate_name": candidate_name,
                "position": position,
                "interview_date": datetime.now().isoformat(),
                "duration_minutes": duration_minutes,
                "evaluator": "SIMA - AI Interview Assistant",
                "evaluation_timestamp": datetime.now().isoformat()
            },
            "candidate_info": candidate_info or {},
            "overall_assessment": ai_assessment.get("overall_assessment", {}),
            "detailed_evaluation": ai_assessment.get("detailed_evaluation", {}),
            "ratings": ai_assessment.get("ratings", {}),
            "strengths": ai_assessment.get("strengths", []),
            "weaknesses": ai_assessment.get("weaknesses", []),
            "red_flags": ai_assessment.get("red_flags", []),
            "key_highlights": ai_assessment.get("key_highlights", []),
            "recommendation": ai_assessment.get("recommendation", {}),
            "feedback_for_candidate": ai_assessment.get("feedback_for_candidate", ""),
            "interview_notes": interview_notes,
            "transcript_summary": ai_assessment.get("transcript_summary", "")
        }
        
        # Save evaluation to file
        filename = self._save_evaluation(evaluation)
        evaluation["metadata"]["saved_to"] = filename
        
        logger.info(f"Evaluation completed and saved: {filename}")
        
        return evaluation
    
    async def _generate_ai_assessment(
        self,
        candidate_name: str,
        position: str,
        transcript: str,
        interview_notes: List[Dict],
        duration_minutes: int
    ) -> Dict:
        """
        Use OpenAI to generate comprehensive AI assessment
        """
        
        # Prepare context for AI
        notes_summary = self._format_notes(interview_notes)
        
        evaluation_prompt = f"""You are an expert hiring manager evaluating an interview. Analyze the following interview data and provide a comprehensive evaluation.

INTERVIEW DETAILS:
- Candidate: {candidate_name}
- Position: {position}
- Duration: {duration_minutes} minutes

INTERVIEW NOTES:
{notes_summary}

INTERVIEW TRANSCRIPT:
{transcript[:4000]}  # Limit transcript length for API

Based on this interview, provide a detailed evaluation in the following JSON format:

{{
    "overall_assessment": {{
        "summary": "2-3 sentence overall impression",
        "hire_recommendation": "Strong Hire / Hire / Maybe / No Hire",
        "confidence_level": "High / Medium / Low",
        "reasoning": "Brief explanation of recommendation"
    }},
    "detailed_evaluation": {{
        "technical_skills": {{
            "rating": 1-10,
            "assessment": "detailed assessment",
            "evidence": ["specific examples from interview"]
        }},
        "problem_solving": {{
            "rating": 1-10,
            "assessment": "detailed assessment",
            "evidence": ["specific examples"]
        }},
        "communication": {{
            "rating": 1-10,
            "assessment": "detailed assessment",
            "evidence": ["specific examples"]
        }},
        "experience_relevance": {{
            "rating": 1-10,
            "assessment": "detailed assessment",
            "evidence": ["specific examples"]
        }},
        "cultural_fit": {{
            "rating": 1-10,
            "assessment": "detailed assessment",
            "evidence": ["specific examples"]
        }}
    }},
    "ratings": {{
        "overall_score": 1-10,
        "technical_competency": 1-10,
        "soft_skills": 1-10,
        "experience_match": 1-10,
        "growth_potential": 1-10
    }},
    "strengths": [
        "List 3-5 key strengths with specific examples"
    ],
    "weaknesses": [
        "List 2-4 areas for improvement with specific examples"
    ],
    "red_flags": [
        "List any concerns or red flags, empty array if none"
    ],
    "key_highlights": [
        "3-5 most impressive or notable moments from the interview"
    ],
    "recommendation": {{
        "decision": "Strong Hire / Hire / Maybe / No Hire",
        "next_steps": "recommended next steps",
        "concerns_to_address": ["any concerns to explore in next rounds"],
        "role_fit_percentage": 0-100
    }},
    "feedback_for_candidate": "Constructive feedback that could be shared with candidate (2-3 paragraphs)",
    "transcript_summary": "Brief summary of interview flow and key discussion points"
}}

Provide ONLY the JSON output, no additional text."""

        try:
            # Call OpenAI API for evaluation
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert hiring manager and interview evaluator. Provide thorough, fair, and data-driven assessments."
                    },
                    {
                        "role": "user",
                        "content": evaluation_prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistent evaluation
                response_format={"type": "json_object"}
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            assessment = json.loads(ai_response)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error generating AI assessment: {e}")
            # Return fallback assessment
            return self._generate_fallback_assessment(interview_notes)
    
    def _format_notes(self, notes: List[Dict]) -> str:
        """Format interview notes for AI consumption"""
        if not notes:
            return "No notes recorded."
        
        formatted = []
        for note in notes:
            category = note.get('category', 'general')
            content = note.get('note', '')
            stage = note.get('stage', 'unknown')
            formatted.append(f"[{category.upper()} - {stage}] {content}")
        
        return "\n".join(formatted)
    
    def _generate_fallback_assessment(self, notes: List[Dict]) -> Dict:
        """Generate basic assessment if AI fails"""
        return {
            "overall_assessment": {
                "summary": "Evaluation based on interview notes",
                "hire_recommendation": "Needs Review",
                "confidence_level": "Low",
                "reasoning": "AI evaluation unavailable, manual review required"
            },
            "detailed_evaluation": {},
            "ratings": {"overall_score": 5},
            "strengths": [],
            "weaknesses": [],
            "red_flags": ["AI evaluation failed - manual review required"],
            "key_highlights": [],
            "recommendation": {
                "decision": "Needs Review",
                "next_steps": "Manual evaluation required",
                "concerns_to_address": [],
                "role_fit_percentage": 50
            },
            "feedback_for_candidate": "Thank you for your time. Our team will review your interview.",
            "transcript_summary": f"Interview conducted with {len(notes)} notes recorded."
        }
    
    def _save_evaluation(self, evaluation: Dict) -> str:
        """Save evaluation to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize candidate name and position for filename
        candidate_name = evaluation["metadata"]["candidate_name"].replace(" ", "_")
        candidate_name = candidate_name.replace("/", "-").replace("\\", "-")  # Remove slashes
        
        position = evaluation["metadata"]["position"].replace(" ", "_")
        position = position.replace("/", "-").replace("\\", "-")  # Remove slashes
        
        filename = f"{candidate_name}_{position}_{timestamp}.json"
        filepath = self.evaluations_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation saved to: {filepath}")
        return str(filepath)
    
    def load_evaluation(self, filename: str) -> Dict:
        """Load a saved evaluation"""
        filepath = self.evaluations_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_evaluations(self) -> List[str]:
        """List all saved evaluations"""
        return [f.name for f in self.evaluations_dir.glob("*.json")]
    
    def generate_summary_report(self, evaluation: Dict) -> str:
        """Generate a human-readable summary report"""
        metadata = evaluation["metadata"]
        overall = evaluation["overall_assessment"]
        ratings = evaluation["ratings"]
        recommendation = evaluation["recommendation"]
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              INTERVIEW EVALUATION REPORT                         ║
╚══════════════════════════════════════════════════════════════════╝

CANDIDATE INFORMATION:
  Name:          {metadata['candidate_name']}
  Position:      {metadata['position']}
  Interview Date: {metadata['interview_date'][:10]}
  Duration:      {metadata['duration_minutes']} minutes

OVERALL ASSESSMENT:
  Recommendation: {overall['hire_recommendation']}
  Confidence:     {overall['confidence_level']}
  Overall Score:  {ratings.get('overall_score', 'N/A')}/10
  Role Fit:       {recommendation.get('role_fit_percentage', 'N/A')}%

SUMMARY:
  {overall['summary']}

REASONING:
  {overall['reasoning']}

RATINGS BREAKDOWN:
  Technical Competency:  {ratings.get('technical_competency', 'N/A')}/10
  Soft Skills:          {ratings.get('soft_skills', 'N/A')}/10
  Experience Match:     {ratings.get('experience_match', 'N/A')}/10
  Growth Potential:     {ratings.get('growth_potential', 'N/A')}/10

STRENGTHS:
"""
        for i, strength in enumerate(evaluation.get('strengths', []), 1):
            report += f"  {i}. {strength}\n"
        
        report += "\nAREAS FOR IMPROVEMENT:\n"
        for i, weakness in enumerate(evaluation.get('weaknesses', []), 1):
            report += f"  {i}. {weakness}\n"
        
        if evaluation.get('red_flags'):
            report += "\n⚠️  RED FLAGS:\n"
            for flag in evaluation['red_flags']:
                report += f"  ⚠️  {flag}\n"
        
        report += f"\nRECOMMENDED NEXT STEPS:\n  {recommendation.get('next_steps', 'N/A')}\n"
        
        report += "\n" + "═" * 68 + "\n"
        
        return report


# Utility function for easy access
async def evaluate_completed_interview(
    candidate_name: str,
    position: str,
    transcript: str,
    interview_notes: List[Dict],
    duration_minutes: int,
    candidate_info: Dict = None
) -> Dict:
    """
    Convenience function to evaluate an interview
    
    Usage:
        evaluation = await evaluate_completed_interview(
            candidate_name="John Doe",
            position="Software Engineer",
            transcript=full_transcript,
            interview_notes=notes_list,
            duration_minutes=30
        )
    """
    evaluator = InterviewEvaluator()
    return await evaluator.evaluate_interview(
        candidate_name=candidate_name,
        position=position,
        transcript=transcript,
        interview_notes=interview_notes,
        duration_minutes=duration_minutes,
        candidate_info=candidate_info
    )