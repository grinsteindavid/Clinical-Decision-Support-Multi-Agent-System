from src.retrievers.base import BaseRetriever


MOCK_TOOLS = [
    {
        "id": 1,
        "name": "Ambient Clinical Documentation AI",
        "category": "Documentation",
        "description": "AI-powered ambient listening for clinical documentation.",
        "target_users": ["physicians", "nurse_practitioners"],
        "problem_solved": "Eliminates documentation burden and reduces burnout.",
        "similarity": 0.85
    },
    {
        "id": 2,
        "name": "Lexicomp Drug Information",
        "category": "Drug Reference",
        "description": "Comprehensive drug database with interaction checking.",
        "target_users": ["pharmacists", "physicians"],
        "problem_solved": "Prevents medication errors and adverse drug interactions.",
        "similarity": 0.72
    },
    {
        "id": 3,
        "name": "Clinical Trial Matching Engine",
        "category": "Research",
        "description": "AI-powered clinical trial matching platform.",
        "target_users": ["research_coordinators", "oncologists"],
        "problem_solved": "Automates clinical trial screening.",
        "similarity": 0.68
    }
]

MOCK_ORGS = [
    {
        "id": 1,
        "name": "Mayo Clinic",
        "org_type": "health_system",
        "specialty": "Multi-specialty",
        "description": "World-renowned academic medical center.",
        "city": "Rochester",
        "state": "Minnesota",
        "ai_use_cases": ["diagnostic_support", "clinical_documentation"],
        "similarity": 0.82
    },
    {
        "id": 2,
        "name": "Cleveland Clinic",
        "org_type": "health_system",
        "specialty": "Cardiology",
        "description": "Leading heart and cardiovascular care center.",
        "city": "Cleveland",
        "state": "Ohio",
        "ai_use_cases": ["ecg_analysis", "risk_prediction"],
        "similarity": 0.75
    },
    {
        "id": 3,
        "name": "Johns Hopkins Hospital",
        "org_type": "academic_medical_center",
        "specialty": "Oncology",
        "description": "Premier cancer treatment and research facility.",
        "city": "Baltimore",
        "state": "Maryland",
        "ai_use_cases": ["tumor_detection", "treatment_planning"],
        "similarity": 0.70
    }
]


class MockToolsRetriever(BaseRetriever):
    """Mock retriever for clinical_tools - no DB connection needed."""
    
    def __init__(self, fixture_data: list[dict] = None):
        self.data = fixture_data if fixture_data is not None else MOCK_TOOLS
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        return self.data[:limit]


class MockOrgsRetriever(BaseRetriever):
    """Mock retriever for clinical_organizations - no DB connection needed."""
    
    def __init__(self, fixture_data: list[dict] = None):
        self.data = fixture_data if fixture_data is not None else MOCK_ORGS
    
    def search(self, query: str, limit: int = 5) -> list[dict]:
        return self.data[:limit]
