from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import re  # <-- ¡Importante! Añade esta línea al inicio

class ValidateCvForm(FormValidationAction):
    """Clase para validar el formulario de creación de CV."""

    def name(self) -> Text:
        """Nombre único del formulario."""
        return "validate_cv_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        """Define los slots requeridos dinámicamente."""
        
        required = [
            "full_name",
            "birth_date",
            "city",
            "timezone",
            "email",
            "wants_phone",
        ]

        if tracker.get_slot("wants_phone") is True:
            required.append("phone_number")

        required.append("wants_linkedin")

        if tracker.get_slot("wants_linkedin") is True:
            required.append("linkedin_profile")

        return required

    # --- Funciones de Validación de Slots ---

    def validate_wants_phone(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida la intención para 'wants_phone'."""
        
        intent = tracker.latest_message['intent'].get('name')
        
        if intent == 'affirm_phone' or intent == 'affirm':
            return {"wants_phone": True}
        
        if intent == 'deny_phone' or intent == 'deny':
            return {"wants_phone": False}
        
        dispatcher.utter_message(text="Por favor, usa los botones 'Sí' o 'No'.")
        return {"wants_phone": None}

    def validate_wants_linkedin(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida la intención para 'wants_linkedin'."""
        
        intent = tracker.latest_message['intent'].get('name')

        if intent == 'affirm':
            return {"wants_linkedin": True}
        
        if intent == 'deny':
            return {"wants_linkedin": False}
        
        dispatcher.utter_message(text="Por favor, usa los botones 'Sí' o 'No'.")
        return {"wants_linkedin": None}

    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida que el email tenga un formato básico."""
        
        # --- CAMBIO: Regex más estricto ---
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        if re.match(email_regex, slot_value):
            return {"email": slot_value}
        else:
            dispatcher.utter_message(text="Eso no parece un email válido. ¿Puedes intentarlo de nuevo? (Ej. tu@correo.com)")
            return {"email": None}

    # --- ¡NUEVO! Validadores para Texto Libre ---
    # Estas funciones le dicen a Rasa que simplemente acepte el texto.
    # -----------------------------------------------------------

    def validate_full_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Simplemente acepta el texto para el nombre."""
        return {"full_name": slot_value}

    def validate_birth_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Simplemente acepta el texto para la fecha."""
        # (Más adelante, podrías validar el formato "DD/MM/AAAA")
        return {"birth_date": slot_value}

    def validate_city(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Simplemente acepta el texto para la ciudad."""
        return {"city": slot_value}

    def validate_timezone(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Simplemente acepta el texto para la zona horaria."""
        return {"timezone": slot_value}

    def validate_phone_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Simplemente acepta el texto para el teléfono."""
        # (Más adelante, podrías validar que solo sean números)
        return {"phone_number": slot_value}

    def validate_linkedin_profile(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Simplemente acepta el texto para linkedin."""
        return {"linkedin_profile": slot_value}

    # -----------------------------------------------------------

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict]:
        """Se llama cuando el formulario se completa."""
        
        dispatcher.utter_message(response="utter_submit_cv_form")
        return []