# ------------------------------------------------------------------------
# CR Jose E Moraes
# AKA Zehn
# ------------------------------------------------------------------------
# Last Update 10 set 2024
# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
import os
from openai import OpenAI, OpenAIError
from app.core.schemas.openai_utils_schemas import OpenAIClientSchema
from app.core.settings.conf import logger




# ------------------------------------------------------------------------
# CREATE CLIENT
#! TODO it must ve balanced in future create a client per LOGGED USER
# ------------------------------------------------------------------------
client_schema_ = OpenAIClientSchema(api_key=os.getenv("OPENAI_NEUROCURSO_API_KEY"), organization=os.getenv("OPENAI_NEUROCURSO_ORGANIZATION_ID"))
def create_client(client_: OpenAIClientSchema=client_schema_):
    """
    Create an OpenAI client instance with the provided assistant configuration.

    Args:
        assistant (OpenAIAssistantSchema): A schema containing OpenAI configuration details.

    Returns:
        OpenAI: An instance of the OpenAI client.

    Raises:
        ValueError: If the API key or organization ID is missing.
        OpenAIError: If there's an error initializing the OpenAI client.
    """
    
    try:
        if not client_.api_key:
            raise ValueError("API key is required")
        
        
        if not client_.organization:
            raise ValueError("Organization ID is required")

        client = OpenAI(
            api_key=client_.api_key, 
            organization=client_.organization,
        )

        
        # Test the connection
        client.models.list()
        
        logger.info("OpenAI client created successfully")
        return client

    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise

    except OpenAIError as oe:
        logger.error(f"OpenAI error: {str(oe)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    import os
    from app.core.settings.conf import ENV_NAME_OPENAI_API_KEY
    from app.core.settings.conf import ENV_NAME_OPENAI_ORG
    try:
        test_client = OpenAIClientSchema(
            api_key=os.getenv(ENV_NAME_OPENAI_API_KEY),
            organization_id=os.getenv(ENV_NAME_OPENAI_ORG),
        )
        client = create_client(test_client)
        print("OpenAI client created successfully")
    except Exception as e:
        print(f"Error creating OpenAI client: {str(e)}")

# ------------------------------------------------------------------------