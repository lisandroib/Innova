from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

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
        """
        Define los slots requeridos dinámicamente.
        Aquí es donde manejamos la lógica condicional.
        """
        
        # Inicia con la lista de slots que SIEMPRE se piden
        required = [
            "full_name",
            "birth_date",
            "city",
            "timezone",
            "email",
            "wants_phone", # Siempre preguntamos si quiere teléfono
        ]

        # Lógica condicional para el teléfono
        if tracker.get_slot("wants_phone") is True:
            # Si el usuario dijo que SÍ, AÑADIMOS 'phone_number' a la lista
            required.append("phone_number")

        # Siempre preguntamos si quiere LinkedIn *después* de lo del teléfono
        required.append("wants_linkedin")

        # Lógica condicional para LinkedIn
        if tracker.get_slot("wants_linkedin") is True:
            # Si el usuario dijo que SÍ, AÑADIMOS 'linkedin_profile'
            required.append("linkedin_profile")

        return required

    # --- Validación de Slots (Opcional pero recomendado) ---

    def validate_wants_phone(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida la intención para 'wants_phone'."""
        
        # Si el usuario dijo "Sí" (payload: /affirm_phone)
        if tracker.latest_message['intent'].get('name') == 'affirm_phone':
            return {"wants_phone": True}
        
        # Si el usuario dijo "No" (payload: /deny_phone)
        if tracker.latest_message['intent'].get('name') == 'deny_phone':
            return {"wants_phone": False}
        
        # Si escribió algo que no es un botón
        dispatcher.utter_message(text="Por favor, usa los botones 'Sí' o 'No'.")
        return {"wants_phone": None} # Vuelve a preguntar

    def validate_wants_linkedin(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Valida la intención para 'wants_linkedin'."""
        
        if tracker.latest_message['intent'].get('name') == 'affirm':
            return {"wants_linkedin": True}
        
        if tracker.latest_message['intent'].get('name') == 'deny':
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
        
        if "@" in slot_value and "." in slot_value:
            # Formato simple OK
            return {"email": slot_value}
        else:
            # Formato inválido
            dispatcher.utter_message(text="Eso no parece un email válido. ¿Puedes intentarlo de nuevo? (Ej. tu@correo.com)")
            return {"email": None} # Vuelve a preguntar por el email

    # --- Envío del Formulario ---

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict]:
        """Se llama cuando el formulario se completa."""
        
        # (Aquí es donde guardarías los datos en una Base de Datos)
        
        dispatcher.utter_message(response="utter_submit_cv_form")
        return []