# Vapi Assistant Setup

This is a dashboard setup reference, not a configuration file consumed by the
backend. The live assistant is configured in Vapi. Keep this guide aligned
with the Vapi dashboard when settings change.

## Values Confirmed in This Repository

- **Phone number:** +1 (320) 703 4084
- **Model:** Google Gemini 2.5 Flash.
- **System prompt:** Use the prompt in [`system_prompt.md`](system_prompt.md).
- **Tools:** Configure the functions in [`tool_schema.json`](tool_schema.json).
	Their server URLs and HTTP methods are defined there.
- **Backend:** `https://voice-patient-registration-uk6t.vercel.app`

The tool definitions call `POST /patients/lookup` to check for an existing
patient, `POST /patients` to register a patient, and `PUT /patients/{patient_id}`
to update one.

## Verify in the Vapi Dashboard

Before recreating or changing the assistant, confirm and record:

- The voice and speech-to-text provider/model.
- That the assistant is assigned to the phone number above.
- That all three functions from `tool_schema.json` are configured with the
	listed URLs and methods.
- That the system prompt matches `system_prompt.md` (use the prompt itself,
	not the design-rationale notes after it).
- Any call behavior or privacy settings required by the deployment.

Do not put API keys, credentials, or patient information in this file. The
Vapi dashboard remains the source of truth for settings not documented here.
