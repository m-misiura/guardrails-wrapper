import os
import subprocess
import time
import importlib
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from guardrails import Guard, OnFailAction
from dotenv import load_dotenv


load_dotenv()


def dynamically_import_detect_pii():
    """Dynamically imports DetectPII, installing the package if necessary."""
    try:

        from guardrails.hub import DetectPII

        return DetectPII
    except ImportError as e:
        print(f"Initial import failed: {e}")

        print("DetectPII not found. Installing the detect_pii package...")
        try:
            subprocess.run(
                ["guardrails", "hub", "install", "hub://guardrails/detect_pii"],
                check=True,
            )

            time.sleep(2)

            if "guardrails.hub" in sys.modules:
                print("Reloading guardrails.hub module...")
                importlib.reload(sys.modules["guardrails.hub"])
            else:
                print("Importing guardrails.hub module afresh...")
                importlib.import_module("guardrails.hub")

            from guardrails.hub import DetectPII

            return DetectPII
        except subprocess.CalledProcessError as e:
            print(f"Installation failed: {e}")
            raise
        except ImportError as e:
            print(f"Failed to import DetectPII even after installation: {e}")
            raise


DetectPII = None
try:
    DetectPII = dynamically_import_detect_pii()
except ImportError:
    print("Could not load DetectPII. Please ensure the package is correctly installed.")

if DetectPII:

    PII_ENTITIES = [
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "DOMAIN_NAME",
        "IP_ADDRESS",
        "DATE_TIME",
        "LOCATION",
        "PERSON",
        "URL",
        "CREDIT_CARD",
        "CRYPTO",
        "IBAN_CODE",
        "NRP",
        "MEDICAL_LICENSE",
        "US_BANK_NUMBER",
        "US_DRIVER_LICENSE",
        "US_ITIN",
        "US_PASSPORT",
        "US_SSN",
    ]

    guard = Guard().use(DetectPII, PII_ENTITIES, on_fail=OnFailAction.EXCEPTION)

    def create_app(test_config=None):
        """Create and configure the Flask application."""
        app = Flask(__name__)
        CORS(app)

        if test_config:
            app.config.from_mapping(test_config)

        @app.route("/validate", methods=["POST"])
        def validate_text():
            input_text = request.json.get("text", "")
            app.logger.debug(f"Input text received: {input_text}")

            try:
                outcome = guard.validate(input_text)
                app.logger.debug(f"Validation outcome: {outcome}")

                if outcome.validation_passed:
                    response = {
                        "result": "Validation passed.",
                        "validated_output": outcome.validated_output,
                    }
                    return jsonify(response), 200
                else:
                    response = {
                        "error": "Validation failed.",
                        "details": outcome.error,
                    }
                    return jsonify(response), 400
            except Exception as e:
                app.logger.error(f"Validation failed with exception: {e}")
                return jsonify({"error": str(e)}), 400

        return app

    if __name__ == "__main__":
        app = create_app()
        app.run(
            debug=True,
            host="0.0.0.0",
            port=int(os.getenv("FLASK_PORT", default="5000")),
        )
else:
    print("App initialization failed due to missing DetectPII class.")
