from fastapi import FastAPI, Request, Response, status
import httpx, os
from fastapi.middleware.cors import CORSMiddleware

PATIENT_API_URL = os.getenv("PATIENT_API_URL", "http://patient_api:8001")
ADMIN_API_URL = os.getenv("ADMIN_API_URL", "http://admin_api:8002")

app = FastAPI(title="Gateway API", version="0.1.0", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def _proxy(request: Request, upstream_base: str, upstream_path: str) -> Response:
    method = request.method
    url = f"{upstream_base}{upstream_path}"

    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)  # ✅ 안전
    body = await request.body()

    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        upstream_response = await client.request(
            method=method,
            url=url,
            headers=headers,
            params=request.query_params,   # ✅ query string 직접 붙이는 것보다 안전
            content=body,
        )

    excluded = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
    response_headers = {
        k: v for k, v in upstream_response.headers.items()
        if k.lower() not in excluded
    }

    # ✅ media_type는 지정하지 않는 게 가장 안전(헤더 그대로 전달)
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )

# root도 프록시되도록 2개 라우트로 분리
# @app.api_route("/api/v1/patient", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
# async def proxy_patient_root(request: Request) -> Response:
#     return await _proxy(request, PATIENT_API_URL, "/api/v1/patient")

@app.api_route("/api/v1/patient/{path:path}", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
async def proxy_patient_api(request: Request, path: str) -> Response:
    if request.method == "OPTIONS":
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return await _proxy(request, PATIENT_API_URL, f"/api/v1/patient/{path}")

# @app.api_route("/api/v1/admin", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
# async def proxy_admin_root(request: Request) -> Response:
#     return await _proxy(request, ADMIN_API_URL, "/api/v1/admin")

@app.api_route("/api/v1/admin/{path:path}", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
async def proxy_admin_api(request: Request, path: str) -> Response:
    if request.method == "OPTIONS":
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return await _proxy(request, ADMIN_API_URL, f"/api/v1/admin/{path}")
