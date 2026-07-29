import json
from fastapi import FastAPI, HTTPException
from app.schemas import JDAnalyzeRequest, ApiResponse
from app.services.prompt_service import build_jd_analyze_prompt
from app.services.llm_service import call_llm

app = FastAPI(title="AI JD Analyzer")


@app.get("/health")
def health():
    return {
        "code": 200,
        "message": "success",
        "data": {
            "status": "ok"
        }
    }


@app.post("/analyze-jd", response_model=ApiResponse)
def analyze_jd(request: JDAnalyzeRequest):
    jd = request.jd.strip()

    if not jd:
        raise HTTPException(status_code=400, detail="JD不能为空")

    prompt = build_jd_analyze_prompt(jd)
    result_text = call_llm(prompt)

    try:
        result_json = json.loads(result_text)
    except json.JSONDecodeError:
        return {
            "code": 500,
            "message": "模型返回内容不是合法JSON",
            "data": result_text
        }

    return {
        "code": 200,
        "message": "success",
        "data": result_json
    }