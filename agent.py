import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('OPEN_ROUTER_API')}",
    "Content-Type": "application/json"
}

EXAMPLES = [
    dict(from_age="60-72", to_age="36-48",
         area_code="TADB", integrated_code="TAB1.2",
         process_code="TAB1.2.SB4", letter="ç"),

    dict(from_age="48-60", to_age="36-48",
         area_code="TAOB", integrated_code="TAB2.2",
         process_code="TAB2.2.SB3", letter="c"),

    dict(from_age="36-48", to_age="60-72",
         area_code="TAEOB", integrated_code="TAEOB1",
         process_code="TAEOB1.1", letter="a")
]

TRANSFORM_REQUESTS = [
    dict(from_age="60-72", to_age="48-60",
         area_code="TADB", integrated_code="TAB1.2",
         process_code="TAB1.2.SB6", letter="e", force_llm=True),

    dict(from_age="48-60", to_age="60-72",
         area_code="TAOB", integrated_code="TAB2.3",
         process_code="TAB2.3.SB1", letter="a"),

    dict(from_age="36-48", to_age="48-60",
         area_code="TADB", integrated_code="TAB1.1",
         process_code="TAB1.1.SB2", letter="b"),

    dict(from_age="60-72", to_age="36-48",
         area_code="TAOB", integrated_code="TAB2.2",
         process_code="TAB2.2.SB4", letter="ç", force_llm=True),

    dict(from_age="48-60", to_age="36-48",
         area_code="TADB", integrated_code="TAB1.2",
         process_code="TAB1.2.SB3", letter="c", force_llm=True),

    dict(from_age="36-48", to_age="60-72",
         area_code="TAKB", integrated_code="TAB3.2",
         process_code="TAB3.2.SB1", letter="a"),

    dict(from_age="60-72", to_age="48-60",
         area_code="TAKB", integrated_code="TAB3.2",
         process_code="TAB3.2.SB7", letter="f", force_llm=True),

    dict(from_age="48-60", to_age="60-72",
         area_code="TAEOB", integrated_code="TAEOB5",
         process_code="TAEOB5.1", letter="a", force_llm=True),

    dict(from_age="36-48", to_age="60-72",
         area_code="TAEOB", integrated_code="TAEOB1",
         process_code="TAEOB1.1", letter="a"),

    dict(from_age="60-72", to_age="48-60",
         area_code="TADB", integrated_code="TAB1.3",
         process_code="TAB1.3.SB2", letter="b", force_llm=True)
]


def _get_sub_learning_outcome(data: dict,
                              age: str,
                              area_code: str,
                              integrated_code: str,
                              process_code: str,
                              letter: str):
    for age_block in data.get("age_ranges", []):
        if age_block["range"] != age:
            continue
        for area in age_block["area_skills"]:
            if area["code"] != area_code:
                continue
            for integ in area["integrated_skills"]:
                if integ["code"] != integrated_code:
                    continue
                for pc in integ["process_components"]:
                    if pc["code"] != process_code:
                        continue
                    for slo in pc["learning_outcome"]["sub_learning_outcomes"]:
                        if slo["letter"] == letter:
                            return slo["text"]
    return None


def transform_sub_outcome(data: dict,
                          from_age: str,
                          to_age: str,
                          area_code: str,
                          integrated_code: str,
                          process_code: str,
                          letter: str,
                          force_llm: bool = False,
                          model: str = "qwen/qwen3-235b-a22b:free"):
    src = _get_sub_learning_outcome(data, from_age, area_code,
                                    integrated_code, process_code, letter)
    tgt = _get_sub_learning_outcome(data, to_age, area_code,
                                    integrated_code, process_code, letter)

    if src is None:
        return None

    if tgt and not force_llm:
        return {"source": src, "target": tgt, "llm_used": False}

    prompt = (
        "Sen bir okul öncesi eğitim uzmanısın. "
        "Aşağıdaki alt öğrenme çıktısını hedef yaş grubuna uygun DÖNÜŞTÜR. "
        "SADECE dönüştürülmüş tek cümleyi yaz, başka açıklama ekleme.\n\n"
        f"Kaynak yaş: {from_age}\n"
        f"Hedef yaş : {to_age}\n"
        f"Metin      : \"{src}\""
    )

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    resp = requests.post(OPENROUTER_URL, headers=HEADERS,
                         data=json.dumps(body), timeout=60)
    resp.raise_for_status()

    raw_reply = resp.json()["choices"][0]["message"]["content"]
    transformed = raw_reply.splitlines()[0].strip().strip("“”\"' ")

    return {"source": src, "target": transformed, "llm_used": True}
