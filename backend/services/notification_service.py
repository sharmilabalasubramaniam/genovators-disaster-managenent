from sqlalchemy.orm import Session
from backend.models import models
from datetime import datetime

class NotificationService:
    @staticmethod
    def create_notification(db: Session, case_id: int, notification_type: str, title: str, message: str, priority: str = "LOW", related_entity_type: str = None, related_entity_id: int = None, recipient_role: str = "OFFICER"):
        notification = models.Notification(
            case_id=case_id,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            recipient_role=recipient_role,
            status="UNREAD",
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def notify_case_created(db: Session, case_id: int, vrn_id: str):
        return NotificationService.create_notification(
            db, case_id, "CASE_CREATED", "New Case Created", f"Family reported missing person. Case VRN: {vrn_id}", "MEDIUM"
        )
        
    @staticmethod
    def notify_match_found(db: Session, case_id: int, vrn_id: str, candidate_vrn: str, score: float):
        priority = "HIGH" if score > 80 else "MEDIUM"
        title = "High-Confidence Potential Match Found" if score > 80 else "Potential Match Found"
        return NotificationService.create_notification(
            db, case_id, "MATCH_FOUND", title, f"Potential match identified for {vrn_id}. Candidate: {candidate_vrn}. Please review verification evidence before taking action.", priority
        )

    @staticmethod
    def notify_verification_started(db: Session, case_id: int, vrn_id: str):
        return NotificationService.create_notification(
            db, case_id, "VERIFICATION_STARTED", "Verification Started", f"Verification started for VRN: {vrn_id}", "LOW"
        )

    @staticmethod
    def notify_evidence_requested(db: Session, case_id: int, vrn_id: str):
        return NotificationService.create_notification(
            db, case_id, "EVIDENCE_REQUESTED", "Evidence Required", f"Additional evidence requested for VRN: {vrn_id}.", "MEDIUM"
        )

    @staticmethod
    def notify_case_verified(db: Session, case_id: int, vrn_id: str):
        return NotificationService.create_notification(
            db, case_id, "VERIFIED_CASE", "Case Verified", f"Case {vrn_id} has been verified. Authorized reunification workflow may proceed.", "HIGH"
        )
        
    @staticmethod
    def notify_case_rejected(db: Session, case_id: int, vrn_id: str):
        return NotificationService.create_notification(
            db, case_id, "REJECTED_CASE", "Case Rejected", f"Verification for Case {vrn_id} has been rejected.", "MEDIUM"
        )
