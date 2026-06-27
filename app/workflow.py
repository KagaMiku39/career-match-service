import json
import os
import re
import urllib.error
import urllib.request

from app.schemas import PromptTemplate, PromptTemplateCreate, WorkflowRunRequest, WorkflowRunResponse
from app.storage import (
    get_prompt_template,
    list_prompt_templates,
    save_prompt_template,
    save_workflow_run,
)


VARIABLE_PATTERN = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


def create_prompt_template(template: PromptTemplateCreate) -> PromptTemplate:
    variables = template.variables or extract_variables(template.user_template)
    template_with_variables = PromptTemplateCreate(
        name=template.name,
        description=template.description,
        system_prompt=template.system_prompt,
        user_template=template.user_template,
        variables=variables,
    )
    template_id = save_prompt_template(template_with_variables)
    saved = get_prompt_template(template_id)
    if saved is None:
        raise RuntimeError("Prompt template was saved but could not be loaded.")
    return saved


def list_templates(limit: int = 50) -> list[PromptTemplate]:
    return list_prompt_templates(limit=limit)


def run_workflow(request: WorkflowRunRequest) -> WorkflowRunResponse:
    template = get_prompt_template(request.template_id)
    if template is None:
        raise ValueError("Prompt template not found.")

    rendered_prompt = render_template(template.user_template, request.inputs)
    missing_variables = [name for name in template.variables if name not in request.inputs]
    if missing_variables:
        rendered_prompt += "\n\nMissing variables: " + ", ".join(missing_variables)

    if request.use_llm and os.getenv("LLM_API_KEY"):
        output = call_llm(template.system_prompt, rendered_prompt)
        mode = "llm" if output is not None else "fallback"
    else:
        output = None
        mode = "template"

    if output is None:
        output = build_template_fallback(template, rendered_prompt, request.inputs)

    return save_workflow_run(
        template_id=template.id,
        inputs=request.inputs,
        rendered_prompt=rendered_prompt,
        output=output,
        mode=mode,
    )


def extract_variables(template_text: str) -> list[str]:
    return list(dict.fromkeys(VARIABLE_PATTERN.findall(template_text)))


def render_template(template_text: str, inputs: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        return inputs.get(name, match.group(0))

    return VARIABLE_PATTERN.sub(replace, template_text)


def build_template_fallback(
    template: PromptTemplate,
    rendered_prompt: str,
    inputs: dict[str, str],
) -> str:
    input_preview = json.dumps(inputs, ensure_ascii=False, indent=2)
    return (
        f"Template '{template.name}' rendered successfully.\n\n"
        f"Rendered prompt:\n{rendered_prompt}\n\n"
        f"Inputs:\n{input_preview}\n\n"
        "LLM_API_KEY is not configured or LLM execution is disabled, so this run returned a local workflow preview."
    )


def call_llm(system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    if not api_key:
        return None

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    http_request = urllib.request.Request(
        base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(http_request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError):
        return None

    try:
        data = json.loads(raw)
        return data["choices"][0]["message"]["content"]
    except (KeyError, TypeError, json.JSONDecodeError):
        return None
