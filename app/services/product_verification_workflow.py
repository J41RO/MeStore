from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.incoming_product_queue import IncomingProductQueue
from app.services.notification_service import NotificationService, NotificationType, NotificationChannel
from app.services.location_assignment_service import LocationAssignmentService, AssignmentStrategy
from app.services.qr_service import QRService

class VerificationStep(str, Enum):
    INITIAL_INSPECTION = "initial_inspection"
    DOCUMENTATION_CHECK = "documentation_check" 
    QUALITY_ASSESSMENT = "quality_assessment"
    LOCATION_ASSIGNMENT = "location_assignment"
    FINAL_APPROVAL = "final_approval"
    COMPLETED = "completed"

class StepResult(BaseModel):
    passed: bool
    notes: str
    issues: List[str] = []
    metadata: Dict[str, Any] = {}

class RejectionReason(str, Enum):
    QUALITY_ISSUES = "quality_issues"
    MISSING_DOCUMENTATION = "missing_documentation"
    DAMAGED_PRODUCT = "damaged_product"
    INCORRECT_DIMENSIONS = "incorrect_dimensions"
    COUNTERFEIT_SUSPECTED = "counterfeit_suspected"
    SAFETY_CONCERNS = "safety_concerns"
    OTHER = "other"

class ProductRejection(BaseModel):
    reason: RejectionReason
    description: str
    quality_score: Optional[int] = None
    evidence_photos: List[str] = []
    inspector_notes: str
    can_appeal: bool = True
    appeal_deadline: Optional[datetime] = None

class ProductVerificationWorkflow:
    def __init__(self, db: Session, queue_item: IncomingProductQueue):
        self.db = db
        self.queue_item = queue_item
        self.notification_service = NotificationService()
        self.location_service = LocationAssignmentService(db)
        self.qr_service = QRService()
        self.steps = list(VerificationStep)
        self.step_order = [
            VerificationStep.INITIAL_INSPECTION,
            VerificationStep.DOCUMENTATION_CHECK,
            VerificationStep.QUALITY_ASSESSMENT,
            VerificationStep.LOCATION_ASSIGNMENT,
            VerificationStep.FINAL_APPROVAL,
            VerificationStep.COMPLETED
        ]
    
    def get_current_step(self) -> VerificationStep:
        """Determinar paso actual basado en verification_status"""
        status = self.queue_item.verification_status
        
        if status == 'PENDING':
            return VerificationStep.INITIAL_INSPECTION
        elif status == 'ASSIGNED':
            return VerificationStep.DOCUMENTATION_CHECK
        elif status == 'IN_PROGRESS':
            return VerificationStep.QUALITY_ASSESSMENT
        elif status == 'QUALITY_CHECK':
            return VerificationStep.LOCATION_ASSIGNMENT
        elif status == 'APPROVED':
            return VerificationStep.FINAL_APPROVAL
        elif status == 'COMPLETED':
            return VerificationStep.COMPLETED
        else:
            return VerificationStep.INITIAL_INSPECTION
    
    def execute_step(self, step: VerificationStep, result: StepResult) -> bool:
        """Ejecutar paso específico y actualizar estado"""
        try:
            # Validar que es el paso correcto
            current_step = self.get_current_step()
            if step != current_step and current_step != VerificationStep.COMPLETED:
                return False
            
            # Actualizar notas de verificación
            existing_notes = self.queue_item.verification_notes or ""
            step_note = f"\n[{step.value.upper()}] {result.notes}"
            if result.issues:
                step_note += f" | Issues: {'; '.join(result.issues)}"
            
            self.queue_item.verification_notes = existing_notes + step_note
            
            # Actualizar quality_score si está en quality_assessment
            if step == VerificationStep.QUALITY_ASSESSMENT and 'quality_score' in result.metadata:
                self.queue_item.quality_score = result.metadata['quality_score']
            
            # Actualizar quality_issues si hay problemas
            if result.issues:
                existing_issues = self.queue_item.quality_issues or ""
                self.queue_item.quality_issues = existing_issues + "; ".join(result.issues)
            
            # Avanzar al siguiente estado si el paso fue exitoso
            if result.passed:
                self._advance_to_next_state(step)
            else:
                # Si falla, marcar como rechazado o en espera según el paso
                if step in [VerificationStep.QUALITY_ASSESSMENT, VerificationStep.FINAL_APPROVAL]:
                    self.queue_item.verification_status = 'REJECTED'
                else:
                    self.queue_item.verification_status = 'ON_HOLD'
            
            # Incrementar intentos de verificación
            self.queue_item.verification_attempts = (self.queue_item.verification_attempts or 0) + 1
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            return False
    
    def _advance_to_next_state(self, current_step: VerificationStep):
        """Avanzar al siguiente estado en el workflow"""
        state_mapping = {
            VerificationStep.INITIAL_INSPECTION: 'ASSIGNED',
            VerificationStep.DOCUMENTATION_CHECK: 'IN_PROGRESS',
            VerificationStep.QUALITY_ASSESSMENT: 'QUALITY_CHECK',
            VerificationStep.LOCATION_ASSIGNMENT: 'APPROVED',
            VerificationStep.FINAL_APPROVAL: 'COMPLETED'
        }
        
        if current_step in state_mapping:
            self.queue_item.verification_status = state_mapping[current_step]
            
            # Si se completa el proceso, marcar timestamps
            if current_step == VerificationStep.FINAL_APPROVAL:
                from datetime import datetime
                self.queue_item.processing_completed_at = datetime.utcnow()
    
    def can_proceed_to_next_step(self) -> bool:
        """Validar si puede avanzar al siguiente paso"""
        current_step = self.get_current_step()
        
        # Si ya está completado, no puede avanzar más
        if current_step == VerificationStep.COMPLETED:
            return False
        
        # Validaciones específicas por paso
        if current_step == VerificationStep.INITIAL_INSPECTION:
            return self.queue_item.assigned_to is not None
        
        elif current_step == VerificationStep.DOCUMENTATION_CHECK:
            return self.queue_item.verification_notes is not None
        
        elif current_step == VerificationStep.QUALITY_ASSESSMENT:
            return self.queue_item.quality_score is not None
        
        elif current_step == VerificationStep.LOCATION_ASSIGNMENT:
            return True  # Siempre puede proceder si llegó aquí
        
        elif current_step == VerificationStep.FINAL_APPROVAL:
            return self.queue_item.quality_score and self.queue_item.quality_score >= 7.0
        
        return True
    
    def get_workflow_progress(self) -> Dict[str, Any]:
        """Obtener progreso completo del workflow"""
        current_step = self.get_current_step()
        current_index = self.step_order.index(current_step)
        progress_percentage = (current_index / len(self.step_order)) * 100
        
        steps_detail = []
        for i, step in enumerate(self.step_order):
            is_current = step == current_step
            is_completed = i < current_index
            
            steps_detail.append({
                'step': step,
                'title': self._get_step_title(step),
                'description': self._get_step_description(step),
                'is_current': is_current,
                'is_completed': is_completed,
                'order': i + 1
            })
        
        return {
            'queue_id': self.queue_item.id,
            'current_step': current_step,
            'progress_percentage': progress_percentage,
            'steps': steps_detail,
            'can_proceed': self.can_proceed_to_next_step(),
            'verification_attempts': self.queue_item.verification_attempts or 0
        }
    
    def _get_step_title(self, step: VerificationStep) -> str:
        """Obtener título legible del paso"""
        titles = {
            VerificationStep.INITIAL_INSPECTION: "Inspección Inicial",
            VerificationStep.DOCUMENTATION_CHECK: "Verificación de Documentos",
            VerificationStep.QUALITY_ASSESSMENT: "Evaluación de Calidad",
            VerificationStep.LOCATION_ASSIGNMENT: "Asignación de Ubicación",
            VerificationStep.FINAL_APPROVAL: "Aprobación Final",
            VerificationStep.COMPLETED: "Completado"
        }
        return titles.get(step, step.value)
    
    def _get_step_description(self, step: VerificationStep) -> str:
        """Obtener descripción del paso"""
        descriptions = {
            VerificationStep.INITIAL_INSPECTION: "Revisar condición física y documentación básica del producto",
            VerificationStep.DOCUMENTATION_CHECK: "Validar que toda la documentación esté completa y correcta",
            VerificationStep.QUALITY_ASSESSMENT: "Evaluar la calidad del producto según estándares establecidos",
            VerificationStep.LOCATION_ASSIGNMENT: "Asignar ubicación física en el almacén",
            VerificationStep.FINAL_APPROVAL: "Revisión final y aprobación para ingreso al inventario",
            VerificationStep.COMPLETED: "Producto verificado y listo para inventario"
        }
        return descriptions.get(step, step.value)
    
    async def reject_product(self, rejection: ProductRejection, inspector_user_id: str) -> bool:
        """Rechazar producto y enviar notificaciones"""
        try:
            # Actualizar estado en base de datos
            self.queue_item.verification_status = "REJECTED"
            self.queue_item.quality_issues = rejection.reason.value
            self.queue_item.verification_notes = rejection.description
            if rejection.quality_score:
                self.queue_item.quality_score = rejection.quality_score
            
            # Crear deadline de apelación si no se especifica
            if rejection.can_appeal and not rejection.appeal_deadline:
                rejection.appeal_deadline = datetime.now() + timedelta(hours=48)
            
            # Obtener información del vendedor
            vendor = self.queue_item.vendor
            if not vendor:
                raise ValueError("Vendedor no encontrado")
            
            # Preparar datos para template
            template_data = {
                "vendor_name": vendor.nombre if hasattr(vendor, 'nombre') else vendor.email,
                "tracking_number": self.queue_item.tracking_number,
                "rejection_reasons": self._format_rejection_reasons(rejection),
                "quality_score": rejection.quality_score or "N/A",
                "rejection_summary": rejection.reason.value.replace('_', ' ').title(),
                "inspector_notes": rejection.inspector_notes,
                "appeal_deadline": rejection.appeal_deadline.strftime("%Y-%m-%d %H:%M") if rejection.appeal_deadline else "48 horas",
                "can_appeal": "Sí" if rejection.can_appeal else "No"
            }
            
            # Enviar notificaciones
            channels = [NotificationChannel.EMAIL]
            if hasattr(vendor, 'telefono') and vendor.telefono:
                channels.append(NotificationChannel.SMS)
                
            success = await self.notification_service.send_notification(
                NotificationType.PRODUCT_REJECTED,
                vendor.email,
                getattr(vendor, 'telefono', None),
                template_data,
                channels
            )
            
            if success:
                # Incrementar intentos de verificación
                self.queue_item.verification_attempts = (self.queue_item.verification_attempts or 0) + 1
                self.db.commit()
                return True
            else:
                self.db.rollback()
                return False
                
        except Exception as e:
            self.db.rollback()
            print(f"Error rechazando producto: {e}")
            return False
    
    def _format_rejection_reasons(self, rejection: ProductRejection) -> str:
        """Formatear razones de rechazo para el template"""
        reasons_map = {
            RejectionReason.QUALITY_ISSUES: "Problemas de calidad detectados",
            RejectionReason.MISSING_DOCUMENTATION: "Documentación faltante o incompleta",
            RejectionReason.DAMAGED_PRODUCT: "Producto dañado durante envío",
            RejectionReason.INCORRECT_DIMENSIONS: "Dimensiones no coinciden con lo declarado",
            RejectionReason.COUNTERFEIT_SUSPECTED: "Sospecha de producto falsificado",
            RejectionReason.SAFETY_CONCERNS: "Preocupaciones de seguridad",
            RejectionReason.OTHER: "Otras razones"
        }
        
        reason_text = reasons_map.get(rejection.reason, "Razón no especificada")
        return f"- {reason_text}\n  Detalles: {rejection.description}"
    
    async def approve_product(self, inspector_user_id: str, quality_score: Optional[int] = None) -> bool:
        """Aprobar producto y enviar notificación"""
        try:
            # Actualizar estado
            self.queue_item.verification_status = "APPROVED"
            if quality_score:
                self.queue_item.quality_score = quality_score
            
            # Obtener vendedor
            vendor = self.queue_item.vendor
            if vendor:
                template_data = {
                    "vendor_name": vendor.nombre if hasattr(vendor, 'nombre') else vendor.email,
                    "tracking_number": self.queue_item.tracking_number,
                    "quality_score": quality_score or "N/A"
                }
                
                # Enviar notificación de aprobación
                channels = [NotificationChannel.EMAIL]
                if hasattr(vendor, 'telefono') and vendor.telefono:
                    channels.append(NotificationChannel.SMS)
                    
                await self.notification_service.send_notification(
                    NotificationType.PRODUCT_APPROVED,
                    vendor.email,
                    getattr(vendor, 'telefono', None),
                    template_data,
                    channels
                )
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error aprobando producto: {e}")
            return False
    
    async def auto_assign_location(self, inspector_user_id: str) -> Dict[str, Any]:
        """Asignar automáticamente ubicación al producto"""
        try:
            # Obtener producto asociado
            product = self.queue_item.product
            if not product:
                raise ValueError("Producto no encontrado")
            
            # Asignar ubicación óptima
            assignment_result = await self.location_service.assign_optimal_location(
                product, self.queue_item
            )
            
            if assignment_result:
                # Actualizar estado del workflow
                self.queue_item.verification_status = "APPROVED"
                
                # Guardar información de ubicación en metadata
                if not self.queue_item.metadata:
                    self.queue_item.metadata = {}
                
                self.queue_item.metadata['assigned_location'] = assignment_result
                self.queue_item.metadata['assigned_by'] = inspector_user_id
                self.queue_item.metadata['assignment_date'] = datetime.utcnow().isoformat()
                
                # Actualizar notas de verificación
                location_info = f"Ubicación asignada automáticamente: {assignment_result['zona']}-{assignment_result['estante']}-{assignment_result['posicion']}"
                if self.queue_item.verification_notes:
                    self.queue_item.verification_notes += f"\n{location_info}"
                else:
                    self.queue_item.verification_notes = location_info
                
                self.db.commit()
                
                return {
                    "success": True,
                    "location": assignment_result,
                    "message": "Ubicación asignada automáticamente"
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontraron ubicaciones disponibles",
                    "suggestion": "Revisar capacidad del almacén"
                }
                
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Error en asignación automática: {str(e)}"
            }
    
    async def suggest_manual_locations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Sugerir ubicaciones para asignación manual"""
        try:
            available_locations = await self.location_service._get_available_locations()
            
            suggestions = []
            for location in available_locations[:limit]:
                suggestions.append({
                    "zona": location["zona"],
                    "estante": location["estante"],
                    "posicion": location.get("posicion", "01"),
                    "capacity": location["available_capacity"],
                    "recommendation": self._get_location_recommendation(location)
                })
            
            return suggestions
        except Exception as e:
            print(f"Error obteniendo sugerencias: {e}")
            return []
    
    def _get_location_recommendation(self, location: Dict[str, Any]) -> str:
        """Obtener recomendación textual para una ubicación"""
        zona = location["zona"]
        capacity = location["available_capacity"]
        
        if zona.startswith('A'):
            return "Zona de fácil acceso, ideal para productos de alta rotación"
        elif zona.startswith('B'):
            return "Zona intermedia, buena para productos de rotación media"
        elif capacity > 10:
            return "Amplia capacidad disponible, ideal para productos grandes"
        else:
            return "Espacio limitado, apropiado para productos pequeños"
    
    async def complete_verification_with_qr(self, inspector_user_id: str) -> Dict[str, Any]:
        """Completar verificación generando QR automáticamente"""
        try:
            # Generar ID interno único
            internal_id = self.qr_service.generate_internal_tracking_id(
                self.queue_item.tracking_number
            )
            
            # Preparar información del producto
            product_info = {
                "name": self.queue_item.product.name if self.queue_item.product else "Producto",
                "category": self.queue_item.product.categoria if self.queue_item.product else "General",
                "sku": self.queue_item.product.sku if self.queue_item.product else None,
                "verification_date": datetime.utcnow().isoformat()
            }
            
            # Generar código QR
            qr_result = self.qr_service.create_qr_code(
                tracking_number=self.queue_item.tracking_number,
                internal_id=internal_id,
                product_info=product_info,
                style="styled"
            )
            
            # Generar etiqueta completa
            label_filepath = self.qr_service.create_product_label(
                tracking_number=self.queue_item.tracking_number,
                internal_id=internal_id,
                product_info=product_info,
                qr_filepath=qr_result["qr_filepath"]
            )
            
            # Actualizar metadata del producto en la cola
            if not self.queue_item.metadata:
                self.queue_item.metadata = {}
            
            self.queue_item.metadata.update({
                "internal_id": internal_id,
                "qr_generated": True,
                "qr_filename": qr_result["qr_filename"],
                "label_filepath": label_filepath,
                "qr_generation_date": datetime.utcnow().isoformat(),
                "generated_by": inspector_user_id
            })
            
            # Actualizar estado final
            self.queue_item.verification_status = "COMPLETED_WITH_QR"
            
            self.db.commit()
            
            return {
                "success": True,
                "internal_id": internal_id,
                "qr_data": qr_result,
                "label_filepath": label_filepath,
                "message": "Verificación completada con QR generado"
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Error generando QR: {str(e)}"
            }
    
    def get_qr_info(self) -> Optional[Dict[str, Any]]:
        """Obtener información del QR si existe"""
        if self.queue_item.metadata and self.queue_item.metadata.get("qr_generated"):
            return {
                "internal_id": self.queue_item.metadata.get("internal_id"),
                "qr_filename": self.queue_item.metadata.get("qr_filename"),
                "generation_date": self.queue_item.metadata.get("qr_generation_date"),
                "has_qr": True
            }
        return {"has_qr": False}
    
    async def regenerate_qr(self, inspector_user_id: str, style: str = "standard") -> Dict[str, Any]:
        """Regenerar QR con nuevo estilo"""
        if not self.queue_item.metadata or not self.queue_item.metadata.get("internal_id"):
            return {"success": False, "message": "No hay ID interno para regenerar QR"}
        
        try:
            internal_id = self.queue_item.metadata["internal_id"]
            product_info = {
                "name": self.queue_item.product.name if self.queue_item.product else "Producto",
                "category": self.queue_item.product.categoria if self.queue_item.product else "General"
            }
            
            # Regenerar QR
            qr_result = self.qr_service.create_qr_code(
                tracking_number=self.queue_item.tracking_number,
                internal_id=internal_id,
                product_info=product_info,
                style=style
            )
            
            # Actualizar metadata
            self.queue_item.metadata.update({
                "qr_filename": qr_result["qr_filename"],
                "qr_regeneration_date": datetime.utcnow().isoformat(),
                "regenerated_by": inspector_user_id
            })
            
            self.db.commit()
            
            return {
                "success": True,
                "qr_data": qr_result,
                "message": "QR regenerado exitosamente"
            }
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Error regenerando QR: {str(e)}"}