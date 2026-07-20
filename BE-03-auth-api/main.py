from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from routes.auth_routes import router as auth_router
from routes.protected_routes import router as protected_router


app = FastAPI(
    title="FlyRank Auth API",
    description="Authentication API using Supabase Auth and JWT",
    version="1.0"
)


# Include routes

app.include_router(auth_router)
app.include_router(protected_router)



# -----------------------------
# Home Route
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "Auth API is running",
        "docs": "/docs"
    }



# -----------------------------
# Swagger JWT Configuration
# -----------------------------

def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema


    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


    openapi_schema["components"]["securitySchemes"] = {

        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }

    }


    for path in openapi_schema["paths"]:

        if (
            path.startswith("/protected")
            or path.startswith("/auth/logout")
        ):

            for method in openapi_schema["paths"][path]:

                openapi_schema["paths"][path][method][
                    "security"
                ] = [
                    {
                        "BearerAuth": []
                    }
                ]


    app.openapi_schema = openapi_schema

    return app.openapi_schema



app.openapi = custom_openapi