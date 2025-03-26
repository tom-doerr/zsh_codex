import os
import sys
from abc import ABC, abstractmethod
from configparser import ConfigParser

CONFIG_DIR = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
CONFIG_PATH = os.path.join(CONFIG_DIR, "zsh_codex.ini")


class BaseClient(ABC):
    """Base class for all clients"""

    api_type: str = None
    system_prompt = (
        "You are a zsh shell expert, please help me complete the following command, "
        "you should only output the completed command, no need to include any other explanation. "
        "Do not put completion in quotes."
    )

    @abstractmethod
    def get_completion(self, full_command: str) -> str:
        pass


class OpenAIClient(BaseClient):
    """
    config keys:
        - api_type="openai"
        - api_key (required)
        - base_url (optional): defaults to "https://api.openai.com/v1".
        - organization (optional): defaults to None
        - model (optional): defaults to "gpt-4o-mini"
        - temperature (optional): defaults to 1.0.
    """

    api_type = "openai"
    default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini")

    def __init__(self, config: dict):
        try:
            from openai import OpenAI
        except ImportError:
            print(
                "OpenAI library is not installed. Please install it using 'pip install openai'"
            )
            sys.exit(1)

        self.config = config
        self.config["model"] = self.config.get("model", self.default_model)
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", self.config.get("api_key")),
            base_url=self.config.get("base_url", "https://api.openai.com/v1"),
            organization=self.config.get("organization"),
        )

    def get_completion(self, full_command: str) -> str:
        response = self.client.chat.completions.create(
            model=self.config["model"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": full_command},
            ],
            temperature=float(self.config.get("temperature", 1.0)),
        )
        return response.choices[0].message.content


class GoogleGenAIClient(BaseClient):
    """
    config keys:
        - api_type="gemeni"
        - api_key (required)
        - model (optional): defaults to "gemini-1.5-pro-latest"
    """

    api_type = "gemeni"
    default_model = os.getenv("GOOGLE_GENAI_DEFAULT_MODEL", "gemini-1.5-pro-latest")

    def __init__(self, config: dict):
        try:
            import google.generativeai as genai
        except ImportError:
            print(
                "Google Generative AI library is not installed. Please install it using 'pip install google-generativeai'"
            )
            sys.exit(1)

        self.config = config
        genai.configure(
            api_key=os.getenv("GOOGLE_GENAI_API_KEY", self.config.get("api_key"))
        )
        self.config["model"] = config.get("model", self.default_model)
        self.model = genai.GenerativeModel(self.config["model"])

    def get_completion(self, full_command: str) -> str:
        chat = self.model.start_chat(history=[])
        prompt = f"{self.system_prompt}\n\n{full_command}"
        response = chat.send_message(prompt)
        return response.text


class GroqClient(BaseClient):
    """
    config keys:
        - api_type="groq"
        - api_key (required)
        - model (optional): defaults to "llama-3.2-11b-text-preview"
        - temperature (optional): defaults to 1.0.
    """

    api_type = "groq"
    default_model = os.getenv("GROQ_DEFAULT_MODEL", "llama-3.2-11b-text-preview")

    def __init__(self, config: dict):
        try:
            from groq import Groq
        except ImportError:
            print(
                "Groq library is not installed. Please install it using 'pip install groq'"
            )
            sys.exit(1)

        self.config = config
        self.config["model"] = self.config.get("model", self.default_model)
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY", self.config.get("api_key"))
        )

    def get_completion(self, full_command: str) -> str:
        response = self.client.chat.completions.create(
            model=self.config["model"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": full_command},
            ],
            temperature=float(self.config.get("temperature", 1.0)),
        )
        return response.choices[0].message.content


class MistralClient(BaseClient):
    """
    config keys:
        - api_type="mistral"
        - api_key (required)
        - model (optional): defaults to "codestral-latest"
        - temperature (optional): defaults to 1.0.
    """

    api_type = "mistral"
    default_model = os.getenv("MISTRAL_DEFAULT_MODEL", "codestral-latest")

    def __init__(self, config: dict):
        try:
            from mistralai import Mistral
        except ImportError:
            print(
                "Mistral library is not installed. Please install it using 'pip install mistralai'"
            )
            sys.exit(1)

        self.config = config
        self.config["model"] = self.config.get("model", self.default_model)
        self.client = Mistral(
            api_key=os.getenv("MISTRAL_API_KEY", self.config.get("api_key"))
        )

    def get_completion(self, full_command: str) -> str:
        response = self.client.chat.complete(
            model=self.config["model"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": full_command},
            ],
            temperature=float(self.config.get("temperature", 1.0)),
        )
        return response.choices[0].message.content


class AmazonBedrock(BaseClient):
    """
    config keys:
        - api_type="bedrock"
        - aws_region (optional): defaults to environment variable AWS_REGION
        - aws_access_key_id (optional): defaults to environment variable AWS_ACCESS_KEY_ID
        - aws_secret_access_key (optional): defaults to environment variable AWS_SECRET_ACCESS_KEY
        - aws_session_token (optional): defaults to environment variable AWS_SESSION_TOKEN
        - model (optional): defaults to "anthropic.claude-3-5-sonnet-20240620-v1:0" or environment variable BEDROCK_DEFAULT_MODEL
        - temperature (optional): defaults to 1.0.
    """

    api_type = "bedrock"
    default_model = os.getenv(
        "BEDROCK_DEFAULT_MODEL", "anthropic.claude-3-5-sonnet-20240620-v1:0"
    )

    def __init__(self, config: dict):
        try:
            import boto3
        except ImportError:
            print(
                "Boto3 library is not installed. Please install it using 'pip install boto3'"
            )
            sys.exit(1)

        self.config = config
        self.config["model"] = self.config.get("model", self.default_model)

        session_kwargs = {
            "region_name": config.get("aws_region"),
            "aws_access_key_id": config.get("aws_access_key_id"),
            "aws_secret_access_key": config.get("aws_secret_access_key"),
            "aws_session_token": config.get("aws_session_token"),
        }
        self.client = boto3.client(
            "bedrock-runtime", **{k: v for k, v in session_kwargs.items() if v}
        )

    def get_completion(self, full_command: str) -> str:
        import json

        messages = [{"role": "user", "content": full_command}]

        # Format request body based on model type
        if "claude" in self.config["model"].lower():
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": self.system_prompt,
                "messages": messages,
                "temperature": float(self.config.get("temperature", 1.0)),
            }
        else:
            raise ValueError(f"Unsupported model: {self.config['model']}")

        response = self.client.invoke_model(
            modelId=self.config["model"], body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]


class ClientFactory:
    api_types = [
        OpenAIClient.api_type,
        GoogleGenAIClient.api_type,
        GroqClient.api_type,
        MistralClient.api_type,
        AmazonBedrock.api_type,
    ]

    @classmethod
    def create(cls):
        config_parser = ConfigParser()

        if not os.path.exists(CONFIG_PATH):
            # Default to OpenAI if config file is absent
            config = {"api_type": "openai", "api_key": os.getenv("OPENAI_API_KEY")}
            if not config["api_key"]:
                print(
                    "API key for OpenAI is missing. Please set the OPENAI_API_KEY environment variable."
                )
                sys.exit(1)
            return OpenAIClient(config)

        config_parser.read(CONFIG_PATH)

        if "service" not in config_parser or "service" not in config_parser["service"]:
            print(
                "Service section or service key is missing in the configuration file."
            )
            sys.exit(1)

        service = config_parser["service"].get("service")
        if not service or service not in config_parser:
            print(
                f"Config for service {service} is not defined in the configuration file."
            )
            sys.exit(1)

        config = {k: v for k, v in config_parser[service].items()}
        if "api_key" not in config:
            config["api_key"] = os.getenv(f"{service.upper()}_API_KEY")
            if not config["api_key"]:
                print(f"API key is missing for the {service} service.")
                sys.exit(1)

        api_type = config.get("api_type")
        if api_type not in cls.api_types:
            print(
                f"Specified API type {api_type} is not one of the supported services {cls.api_types}."
            )
            sys.exit(1)

        client_classes = {
            OpenAIClient.api_type: OpenAIClient,
            GoogleGenAIClient.api_type: GoogleGenAIClient,
            GroqClient.api_type: GroqClient,
            MistralClient.api_type: MistralClient,
            AmazonBedrock.api_type: AmazonBedrock,
        }

        return client_classes[api_type](config)
