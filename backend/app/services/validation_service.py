import json
from typing import List, Dict, Any
from app.schemas.request import ExpectedDocumentBase

# Mock implementation for Azure Foundry NLP parsing
class ValidationService:
    async def analyze_unstructured_request(self, request_explanation: str) -> List[ExpectedDocumentBase]:
        """
        Calls Azure Foundry to parse the unstructured text into a list of required documents
        and their validation rules.
        """
        # TODO: Implement real Azure Foundry API call here using az login / Azure Identity
        # For now, we return a mocked response based on simple keyword matching or just a default
        
        documents = []
        lower_exp = request_explanation.lower()
        
        if "w2" in lower_exp or "w-2" in lower_exp:
            documents.append(ExpectedDocumentBase(
                document_type="W-2",
                validation_rules={"required_fields": ["EmployerName", "Wages"]}
            ))
        
        if "driver" in lower_exp or "license" in lower_exp:
             documents.append(ExpectedDocumentBase(
                document_type="Driver License",
                validation_rules={"required_fields": ["DocumentNumber", "ExpirationDate", "DateOfBirth"]}
            ))
            
        if not documents:
            # Fallback
            documents.append(ExpectedDocumentBase(
                document_type="Other Document",
                validation_rules={}
            ))
            
        return documents

validation_service = ValidationService()
