from fastapi import FastAPI

app = FastAPI(
    title="MeStore API",
    description="API para gestión de tienda online", 
    version="1.0.0"
)

@app.get("/")
async def root():
    """Endpoint de prueba"""
    return {"message": "Bienvenido a MeStore API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check para monitoreo"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
