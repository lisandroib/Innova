from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import re
# ¡Asegúrate de que estos imports estén al principio de tu archivo!
from rasa_sdk.events import SessionStarted, ActionExecuted

# Esta es nuestra "lista negra" de palabras que SON comandos
# (a diferencia de los intents, que pueden ser erróneos)
COMMAND_TEXT = ['sí', 'si', 'no', 'dale', 'claro', 'bueno', 'negar', 'parar']

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
            "full_name", "birth_date", "city", "timezone",
            "email", "wants_phone",
        ]

        if tracker.get_slot("wants_phone") is True:
            required.append("phone_number")

        required.append("wants_linkedin")

        if tracker.get_slot("wants_linkedin") is True:
            required.append("linkedin_profile")

        return required

    # --- NUEVA LÓGICA DE VALIDACIÓN ---

    def validate_text_slot(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        slot_name: Text
    ) -> Dict[Text, Any]:
        """
        Función genérica para validar texto.
        Rechaza el texto SOLO si el texto parece un comando.
        """
        text = tracker.latest_message.get('text', '').lower()

        if text in COMMAND_TEXT:
            # El usuario *realmente* escribió "sí" o "no"
            dispatcher.utter_message(text=f"Por favor, ingresa un valor válido para {slot_name}.")
            return {slot_name: None}
        
        # Si el texto NO es un comando (ej. "lisandro"),
        # lo aceptamos, INCLUSO SI el NLU se confundió.
        return {slot_name: slot_value}

    def validate_full_name(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        return self.validate_text_slot(slot_value, dispatcher, tracker, domain, "full_name")

    def validate_birth_date(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        return self.validate_text_slot(slot_value, dispatcher, tracker, domain, "birth_date")

    def validate_city(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        return self.validate_text_slot(slot_value, dispatcher, tracker, domain, "city")

    def validate_timezone(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        return self.validate_text_slot(slot_value, dispatcher, tracker, domain, "timezone")

    def validate_phone_number(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        return self.validate_text_slot(slot_value, dispatcher, tracker, domain, "phone_number")

    def validate_linkedin_profile(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        return self.validate_text_slot(slot_value, dispatcher, tracker, domain, "linkedin_profile")

    # --- Validaciones de Lógica Especial ---

    def validate_email(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida que el email tenga un formato básico."""
        
        text = tracker.latest_message.get('text', '').lower()
        if text in COMMAND_TEXT:
            dispatcher.utter_message(text="Por favor, ingresa tu email.")
            return {"email": None}

        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        if re.match(email_regex, str(slot_value)):
            return {"email": slot_value}
        else:
            dispatcher.utter_message(text="Eso no parece un email válido. ¿Puedes intentarlo de nuevo? (Ej. tu@correo.com)")
            return {"email": None}

    def validate_wants_phone(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
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
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida la intención para 'wants_linkedin'."""
        intent = tracker.latest_message['intent'].get('name')
        if intent == 'affirm':
            return {"wants_linkedin": True}
        if intent == 'deny':
            return {"wants_linkedin": False}
        dispatcher.utter_message(text="Por favor, usa los botones 'Sí' o 'No'.")
        return {"wants_linkedin": None}

    def submit(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
    ) -> List[Dict]:
        """Se llama cuando el formulario se completa."""
        dispatcher.utter_message(response="utter_submit_cv_form")
        return []

# --- Esta es la clase que arregla tu saludo inicial ---
class ActionSessionStart(Action):
    """Sobrescribe la acción de inicio de sesión por defecto."""

    def name(self) -> Text:
        return "action_session_start"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        
        events = [SessionStarted()]
        dispatcher.utter_message(response="utter_ask_initial_choice")
        events.append(ActionExecuted("action_listen"))

        return events