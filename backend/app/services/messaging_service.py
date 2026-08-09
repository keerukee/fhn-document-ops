from confluent_kafka import Producer
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class MessagingService:
    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.topic = settings.KAFKA_UPLOAD_TOPIC
        self.producer = None
        
        if self.bootstrap_servers:
            try:
                self.producer = Producer({'bootstrap.servers': self.bootstrap_servers})
            except Exception as e:
                logger.error(f"Failed to initialize Kafka Producer: {e}")
                
    def publish_upload_event(self, request_id: str, document_id: str, blob_url: str, validation_results: dict):
        """
        Publishes a Kafka event notifying the internal app that files are uploaded
        and validated, including the blob storage URL.
        """
        if not self.producer:
            logger.warning("Kafka Producer not configured. Mocking event publish.")
            logger.info(f"Mock Published to {self.topic}: req={request_id}, doc={document_id}, url={blob_url}")
            return
            
        event_data = {
            "request_id": request_id,
            "document_id": document_id,
            "blob_url": blob_url,
            "validation_results": validation_results,
            "status": "PROCESSED"
        }
        
        try:
            self.producer.produce(
                self.topic,
                key=request_id.encode('utf-8'),
                value=json.dumps(event_data).encode('utf-8'),
                callback=self._delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to publish Kafka event: {e}")

    def publish_request_completed_event(self, request_id: str, all_valid: bool):
        """
        Publishes a Kafka event notifying the internal app that all documents for a
        request have been uploaded and processed.
        """
        if not self.producer:
            logger.warning("Kafka Producer not configured. Mocking event publish.")
            logger.info(f"Mock Published to {self.topic}: req={request_id}, ALL_DONE, all_valid={all_valid}")
            return
            
        event_data = {
            "request_id": request_id,
            "status": "REQUEST_COMPLETED",
            "all_valid": all_valid
        }
        
        try:
            self.producer.produce(
                self.topic,
                key=request_id.encode('utf-8'),
                value=json.dumps(event_data).encode('utf-8'),
                callback=self._delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to publish Kafka request completed event: {e}")

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")
            
    def flush(self):
        if self.producer:
            self.producer.flush()

messaging_service = MessagingService()
