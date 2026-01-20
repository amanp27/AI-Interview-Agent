"""
Example script showing how to manually trigger evaluation
Useful for testing or re-evaluating past interviews
"""

import asyncio
from evaluation import InterviewEvaluator

async def main():
    # Example interview data
    candidate_name = "John Doe"
    position = "Senior Software Engineer"
    
    # Example transcript (in real scenario, this comes from interview_tools)
    transcript = """
Interviewer: Hello, I am your Interview Assistant SIMA from Tacktile System. Let's begin - tell me about yourself and your background.

Candidate: Hi, I'm John Doe. I have 5 years of experience in software development, primarily working with Python and Django. I've been working at XYZ Corp for the last 3 years where I lead a team of 4 developers building scalable web applications.

Interviewer: That's interesting. Tell me more about your work at XYZ Corp. What kind of applications did you build?

Candidate: We built a SaaS platform for inventory management. My main responsibility was designing the backend architecture using microservices. I used Django for the APIs, PostgreSQL for the database, and Redis for caching. We also integrated with third-party logistics APIs.

Interviewer: What was your specific role in the microservices architecture?

Candidate: I designed the service boundaries and implemented the authentication service and the inventory service. I also set up the CI/CD pipeline using GitHub Actions and deployed everything on AWS using ECS.

Interviewer: Can you describe a challenging technical problem you faced?

Candidate: Sure. We had a performance issue where database queries were taking 5-10 seconds during peak hours. I analyzed the query patterns, added proper indexing, implemented database connection pooling, and introduced Redis caching for frequently accessed data. This reduced response times to under 500ms.

Interviewer: What did you learn from that experience?

Candidate: I learned the importance of performance monitoring from day one. Now I always set up APM tools early in the project and use database query analyzers to catch issues before they become critical.

Interviewer: Thanks for your time. We'll be in touch.

Candidate: Thank you for the opportunity!
"""
    
    # Example interview notes (in real scenario, this comes from interview_tools)
    interview_notes = [
        {
            "category": "technical",
            "note": "Strong backend experience with Python/Django",
            "stage": "background"
        },
        {
            "category": "technical",
            "note": "Good understanding of microservices architecture",
            "stage": "technical"
        },
        {
            "category": "experience",
            "note": "Led team of 4 developers, 3 years at current company",
            "stage": "background"
        },
        {
            "category": "technical",
            "note": "Hands-on with AWS, CI/CD, Redis, PostgreSQL",
            "stage": "technical"
        },
        {
            "category": "problem_solving",
            "note": "Demonstrated systematic approach to performance issues",
            "stage": "behavioral"
        }
    ]
    
    duration_minutes = 15
    
    candidate_info = {
        "name": candidate_name,
        "position": position,
        "experience_years": 5,
        "current_company": "XYZ Corp"
    }
    
    # Create evaluator and generate assessment
    evaluator = InterviewEvaluator()
    
    print("Starting evaluation...\n")
    
    evaluation = await evaluator.evaluate_interview(
        candidate_name=candidate_name,
        position=position,
        transcript=transcript,
        interview_notes=interview_notes,
        duration_minutes=duration_minutes,
        candidate_info=candidate_info
    )
    
    # Print summary report
    report = evaluator.generate_summary_report(evaluation)
    print(report)
    
    # Access specific parts of evaluation
    print("\n🎯 KEY INSIGHTS:")
    print(f"Overall Score: {evaluation['ratings']['overall_score']}/10")
    print(f"Recommendation: {evaluation['recommendation']['decision']}")
    print(f"Role Fit: {evaluation['recommendation']['role_fit_percentage']}%")
    
    print("\n💪 TOP STRENGTHS:")
    for strength in evaluation['strengths'][:3]:
        print(f"  • {strength}")
    
    print("\n⚠️ AREAS TO IMPROVE:")
    for weakness in evaluation['weaknesses']:
        print(f"  • {weakness}")
    
    if evaluation['red_flags']:
        print("\n🚩 RED FLAGS:")
        for flag in evaluation['red_flags']:
            print(f"  • {flag}")
    
    print(f"\n✅ Evaluation saved to: {evaluation['metadata']['saved_to']}")

if __name__ == "__main__":
    asyncio.run(main())