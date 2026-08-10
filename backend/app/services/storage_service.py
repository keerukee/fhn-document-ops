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
            logger.info(f"MOCK MODE: Simulating upload for {file_name} to local Storage.")
            upload_dir = os.path.join(os.getcwd(), "uploads", request_id)
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(file_content)
                
            return f"local://uploads/{request_id}/{file_name}"
            
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

    async def download_document(self, blob_url: str) -> bytes:
        """
        Downloads a document from Azure Blob Storage given its URL.
        """
        if settings.USE_MOCK_STORAGE or not self.connection_string:
            logger.info(f"MOCK MODE: Simulating download for {blob_url}")
            if blob_url.startswith("local://"):
                file_path = os.path.join(os.getcwd(), blob_url.replace("local://", "").replace("/", os.sep))
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        return f.read()
            return b"MOCK_DOCUMENT_CONTENT"
            
        try:
            # We construct a blob client from the full blob URL and connection string
            # Normally, you might parse the URL to get the container and blob name.
            # Azure Blob URL format: https://<account>.blob.core.windows.net/<container>/<blob_name>
            
            # Simple parsing: 
            # url_parts = blob_url.split('/')
            # container_name = url_parts[3]
            # blob_name = '/'.join(url_parts[4:])
            # Or simpler, if we assume container is known:
            # blob_name = blob_url.split(f"/{self.container_name}/")[-1]
            
            blob_name = blob_url.split(f"/{self.container_name}/")[-1]
            blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            
            download_stream = await blob_client.download_blob()
            return await download_stream.readall()
        except Exception as e:
            logger.error(f"Failed to download document from Azure Blob Storage: {e}")
            raise

storage_service = StorageService()
