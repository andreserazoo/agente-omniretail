from __future__ import annotations

from core.bedrock_client import generate_bedrock_text, is_bedrock_configured


def build_policy_answer(policy_result: dict) -> str:
    results = policy_result.get("results", [])
    if not results:
        return "No encontré una sección de política suficientemente relevante para tu consulta."

    top_result = results[0]
    source_file = str(top_result.get("source_file", "documento de políticas")).strip()
    section_title = str(top_result.get("section_title", "Sección relevante")).strip()
    content = str(top_result.get("content", "")).strip()

    cleaned_content = " ".join(content.split())
    preview = cleaned_content[:700].strip()
    if len(cleaned_content) > 700:
        preview += "..."

    if is_bedrock_configured():
        prompt = (
            "Resume y explica de forma clara una política de e-commerce en español. "
            "No inventes información. "
            "Mantén el contenido fiel al texto fuente. "
            "No uses markdown. "
            "No uses listas, negritas ni viñetas. "
            "Responde en 2 o 3 frases como máximo, con redacción limpia. "
            "Siempre menciona el archivo y la sección.\n\n"
            f"Archivo: {source_file}\n"
            f"Sección: {section_title}\n"
            f"Contenido fuente: {preview}"
        )
        bedrock_text = generate_bedrock_text(
            prompt,
            max_tokens=180,
            temperature=0.1,
        )
        if bedrock_text:
            return bedrock_text

    return (
        f"Según {source_file}, en la sección \"{section_title}\", encontré esto:\n\n"
        f"{preview}"
    )
