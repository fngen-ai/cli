def webapp(framework='fastapi', compute='server'):
    """
    Deploy a fastapi app. Example:

    @webapp(framework='fastapi', compute='server')
    def my_fastapi_app():
        app = FastAPI()
        @app.get("/")
        async def read_root():
            return {"message": "Hello, World!"}
        return app
    """
    def g(f):
        # intentionally do nothing :)
        return f
    return g


def task_worker(compute='server'):
    """
    Coming soon
    """
    def g(f):
        # intentionally do nothing :)
        return f
    return g
