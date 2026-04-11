from __future__ import annotations


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

    return (
        f"Según {source_file}, en la sección \"{section_title}\", encontré esto:\n\n"
        f"{preview}"
    )