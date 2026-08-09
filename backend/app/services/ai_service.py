import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.endpoint = settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
        self.key = settings.AZURE_DOCUMENT_INTELLIGENCE_KEY
        self.client = None
        
        if self.endpoint and self.key:
            try:
                self.client = DocumentIntelligenceClient(
                    endpoint=self.endpoint,
                    credential=AzureKeyCredential(self.key)
                )
            except Exception as e:
                logger.error(f"Failed to initialize Azure Document Intelligence Client: {e}")

    async def extract_data_from_document(self, blob_url: str) -> dict:
        """
        Extracts data from the given blob URL using Azure Document Intelligence.
        """
        if not self.client:
            logger.warning("Azure Document Intelligence Client not configured. Returning mock extraction data.")
            return {"mock_extraction": True, "fields": {"EmployerName": "First Horizon Bank"}}
            
        try:
            # We use begin_analyze_document_from_url which returns an LRO poller
            # In a real async scenario, we'd wrap this properly or use the async client if available
            poller = self.client.begin_analyze_document(
                "prebuilt-document", 
                body={"urlSource": blob_url}
            )
            result: AnalyzeResult = poller.result()
            
            # Simple conversion of result to dict for demonstration
            extracted_data = {}
            if result.documents:
                for doc in result.documents:
                    for name, field in doc.fields.items():
                        extracted_data[name] = field.value_string
                        
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error during Document Intelligence extraction: {e}")
            raise

ai_service = AIService()
