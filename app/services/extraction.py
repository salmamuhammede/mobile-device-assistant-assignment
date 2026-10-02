# Standard library
import json
import os

# Third-party
from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

# Local
from app.configs.config import SUSPICIOUS_PHRASES
from app.prompts.templates import SYSTEM_PROMPT, USER_PROMPT
from app.schema.device import Device

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

MODEL_NAME = os.getenv("LLM_MODEL_NAME", "openrouter/free")


def check_prompt_injection(text: str) -> None:
    """Reject inputs containing common prompt-injection phrases."""
    logger.info("Checking prompt injections is starting ...")
    text_lower = text.lower()

    for phrase in SUSPICIOUS_PHRASES:
        if phrase in text_lower:
            logger.error("Suspicious input detected.")
            raise ValueError("Suspicious input detected.")

    logger.success("Checking prompt injections has completed successfully ...")


def extract_device(text: str) -> Device:
    """Extract structured device information using an LLM."""
    check_prompt_injection(text)

    user_prompt = USER_PROMPT.format(device_text=text)

    validation_error = None

    for attempt in range(3):
        try:
            if validation_error:
                user_prompt = (
                    USER_PROMPT.format(device_text=text)
                    + f"\n\nPrevious validation error:\n{validation_error}"
                    + "\nReturn corrected JSON only."
                )

            logger.info("Extraction attempt {}", attempt + 1)

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("LLM returned an empty response.")

            data = json.loads(content)

            device = Device.model_validate(data)

            logger.info("Device extraction successful")

            return device

        except (json.JSONDecodeError, ValueError) as exc:
            validation_error = str(exc)
            logger.warning(
                "Extraction attempt {} failed: {}",
                attempt + 1,
                validation_error,
            )

    raise ValueError(
        f"Could not extract a valid device after 3 attempts. "
        f"Last error: {validation_error}"
    )


def main():
    logger.info("Testing device extraction...")

    text = (
        "I got a new Samsung Galaxy S24 Ultra. "
        "It is a flagship phone released in 2024. "
        "It has a 6.8 inch Dynamic AMOLED display, "
        "5000 mAh battery, and 200MP camera."
    )

    device = extract_device(text)

    print("\nExtracted device:")
    print(device)

    print("\nAs JSON:")
    print(device.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
