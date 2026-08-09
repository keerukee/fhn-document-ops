import os
from azure.storage.blob.aio import BlobServiceClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        
    async def upload_document(self, file_name: str, file_content: bytes, request_id: str) -> str:
        """
        Uploads a document to Azure Blob Storage and returns the Blob URL.
        """
        if settings.USE_MOCK_STORAGE or not self.connection_string:
            logger.info(f"MOCK MODE: Simulating upload for {file_name} to Blob Storage.")
            # In mock mode, we just return a fake URL so the DB and UI flow works normally.
            return f"https://mockstorage.blob.core.windows.net/{self.container_name}/{request_id}/{file_name}"
            
        try:
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            async with blob_service_client:
                container_client = blob_service_client.get_container_client(self.container_name)
                
                # Create container if it does not exist
                if not await container_client.exists():
                    await container_client.create_container()
                
                blob_name = f"{request_id}/{file_name}"
                blob_client = container_client.get_blob_client(blob_name)
                
                await blob_client.upload_blob(file_content, overwrite=True)
                return blob_client.url
        except Exception as e:
            logger.error(f"Failed to upload document to Azure Blob Storage: {e}")
            raise

storage_service = StorageService()
