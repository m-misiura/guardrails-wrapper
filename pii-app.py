import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from guardrails import Guard, OnFailAction
from guardrails.hub import DetectPII

# Define all PII entities
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

# Initialize the PII guard
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
        debug=True, host="0.0.0.0", port=int(os.getenv("FLASK_PORT", default="5000"))
    )
