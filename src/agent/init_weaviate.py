import os
from dotenv import load_dotenv
import weaviate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_weaviate import WeaviateVectorStore

# --- Default Configuration ---
DEFAULT_WEAVIATE_URL = "http://localhost:8080"
DEFAULT_WEAVIATE_COLLECTION_NAME = "SavaCollection"
DEFAULT_WEAVIATE_TEXT_KEY = "text"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"


def initialize_rag_components(
        openai_api_key: str = None,
        weaviate_url: str = None,
        weaviate_collection_name: str = None,
        weaviate_text_key: str = None,
        embedding_model_name: str = None,
):
    """
    Initializes and returns the core components for a RAG (Retrieval Augmented Generation) system.

    This function sets up:
    1. OpenAI API Key (from argument or environment variable).
    2. OpenAI Embedding Model.
    3. OpenAI Chat Model for generation.
    4. Weaviate client and connection.
    5. WeaviateVectorStore.

    Args:
        openai_api_key (str, optional): OpenAI API key. If None, attempts to load from "OPENAI_API_KEY" env variable.
        weaviate_url (str, optional): URL for the Weaviate instance. Defaults to DEFAULT_WEAVIATE_URL.
        weaviate_collection_name (str, optional): Name of the collection in Weaviate. Defaults to DEFAULT_WEAVIATE_COLLECTION_NAME.
        weaviate_text_key (str, optional): The text key used in the Weaviate schema. Defaults to DEFAULT_WEAVIATE_TEXT_KEY.
        embedding_model_name (str, optional): Name of the OpenAI embedding model. Defaults to DEFAULT_EMBEDDING_MODEL.
        generation_model_name (str, optional): Name of the OpenAI generation model. Defaults to DEFAULT_GENERATION_MODEL.

    Returns:
        tuple: A tuple containing:
            - weaviate_vector_store (WeaviateVectorStore): The initialized vector store.
            - generation_llm (ChatOpenAI): The initialized generation LLM.
            - weaviate_client (weaviate.Client): The Weaviate client instance.
            - embedding_model (OpenAIEmbeddings): The initialized embedding model.

    Raises:
        ValueError: If OPENAI_API_KEY is not provided as an argument and not found in environment variables.
        ConnectionError: If connection to Weaviate fails.
    """
    print("Initializing RAG components...")

    # Load environment variables from .env file if present
    load_dotenv()

    # --- Get OpenAI API Key ---
    api_key = openai_api_key if openai_api_key else os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please provide it as an argument or set it in your environment variables."
        )
    print("OpenAI API Key loaded.")

    # --- Resolve Configurations ---
    resolved_weaviate_url = weaviate_url or os.getenv("WEAVIATE_URL", DEFAULT_WEAVIATE_URL)
    resolved_collection_name = weaviate_collection_name or DEFAULT_WEAVIATE_COLLECTION_NAME  # Using global from user snippet
    resolved_text_key = weaviate_text_key or DEFAULT_WEAVIATE_TEXT_KEY  # Using global from user snippet
    resolved_embedding_model = embedding_model_name or DEFAULT_EMBEDDING_MODEL

    # --- Initialize Embedding Model ---
    print(f"Initializing embedding model: {resolved_embedding_model}...")
    embedding_model = OpenAIEmbeddings(
        api_key=api_key, model=resolved_embedding_model
    )
    print("Embedding model initialized.")


    # --- Initialize Weaviate Client ---
    print(f"Attempting to connect to Weaviate at {resolved_weaviate_url}...")
    # The user's snippet uses weaviate.connect_to_local.
    # Assuming 'localhost' and port 8080 if weaviate_url is like 'http://localhost:8080'
    # For more general URLs, weaviate.connect_to_custom might be better,
    # but let's stick to connect_to_local if that's the typical setup.
    # We'll parse the host and port if possible, otherwise fall back.

    client_to_connect = None
    try:
        if "://" in resolved_weaviate_url:
            protocol, rest = resolved_weaviate_url.split("://", 1)
            host_port = rest.split(":", 1)
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 8080  # Default port for http
            if protocol == "https":
                port = int(host_port[1]) if len(host_port) > 1 else 443  # Default port for https

            print(f"Connecting to Weaviate: host='{host}', port={port}, protocol='{protocol}'")

            # Check if it's a local connection based on common local hostnames
            if host in ["localhost", "127.0.0.1"] and protocol == "http":
                client_to_connect = weaviate.connect_to_local(host=host, port=port)
            else:  # Fallback to custom connection for other URLs or HTTPS
                headers = {}  # Add API key header if needed for cloud services
                # Example for Weaviate Cloud Services (WCS)
                # if os.getenv("WEAVIATE_API_KEY"):
                #    headers["X-OpenAI-Api-Key"] = api_key # Or your Weaviate API key

                client_to_connect = weaviate.connect_to_custom(
                    http_host=host,
                    http_port=port,
                    http_secure=protocol == "https",
                    # grpc_host=host,  # Configure GRPC if used
                    # grpc_port=50051, # Default GRPC port
                    # grpc_secure=protocol == "https",
                    headers=headers
                )

        else:  # Assuming it's just 'hostname' or 'hostname:port'
            host_port = resolved_weaviate_url.split(":", 1)
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 8080
            print(f"Connecting to Weaviate (local default): host='{host}', port={port}")
            client_to_connect = weaviate.connect_to_local(host=host, port=port)

    except Exception as e:
        raise ConnectionError(
            f"Failed to parse Weaviate URL '{resolved_weaviate_url}' or establish connection parameters: {e}")

    if not client_to_connect or not client_to_connect.is_ready():
        raise ConnectionError(
            f"Failed to connect to Weaviate at {resolved_weaviate_url}. Ensure it's running and accessible."
        )
    print("Successfully connected to Weaviate.")
    weaviate_client_instance = client_to_connect  # Assign the connected client

    # --- Initialize Vector Store ---
    print(
        f"Initializing WeaviateVectorStore for collection '{resolved_collection_name}' with text key '{resolved_text_key}'...")
    vector_store = WeaviateVectorStore(
        client=weaviate_client_instance,
        index_name=resolved_collection_name,
        text_key=resolved_text_key,
        embedding=embedding_model,
        # attributes=["source", "document_id"] # Example: if you want to store metadata
    )
    print("WeaviateVectorStore initialized.")

    print("RAG components initialization complete.")
    return vector_store, weaviate_client_instance, embedding_model


# --- Example Usage (Illustrative) ---
if __name__ == "__main__":
    # These would be defined in your main script or loaded from config
    WEAVIATE_URL = os.getenv("WEAVIATE_URL", DEFAULT_WEAVIATE_URL)
    WEAVIATE_COLLECTION_NAME = "MyNewCollection"  # Example: Overriding default
    WEAVIATE_TEXT_KEY = "content"  # Example: Overriding default

    print("Starting RAG component setup from example usage...")

    # Create a dummy .env file for testing if it doesn't exist
    if not os.path.exists("../../../.env"):
        print("Creating a dummy .env file for example. Please replace with your actual OPENAI_API_KEY.")
        with open("../../../.env", "w") as f:
            f.write("OPENAI_API_KEY=your_actual_openai_api_key_here\n")
            f.write(f"WEAVIATE_URL={DEFAULT_WEAVIATE_URL}\n")  # Example for .env

    try:
        # Call the function to get the initialized components
        # You can pass specific values or let it use environment variables/defaults
        my_vector_store, my_weaviate_client, my_embedding_model = initialize_rag_components(
            weaviate_collection_name=WEAVIATE_COLLECTION_NAME,
            weaviate_text_key=WEAVIATE_TEXT_KEY
            # openai_api_key="sk-...", # Optionally pass directly
            # weaviate_url="http://another-weaviate:8080" # Optionally pass directly
        )

        print("\n--- Components Initialized Successfully ---")
        print(f"Vector Store Client: {type(my_vector_store.client)}")
        print(f"Vector Store Index Name: {my_vector_store.index_name}")
        print(f"Weaviate Client Connected: {my_weaviate_client.is_ready()}")
        print(f"Embedding Model: {my_embedding_model.model}")
    except Exception as e:
        print(e)
