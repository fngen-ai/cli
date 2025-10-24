from fngen import Fleet, webapp

from fastapi import FastAPI

my_fleet = Fleet(
    name='my_fleet',
    size='xs',
    region='us-west'
)

@webapp(hostname='live_fastapi.staging.fngen.ai', 
        framework='fastapi', 
        fleet=my_fleet)
def live_fastapi():
    api = FastAPI()

    @api.get('/')
    def index():
        return 'FastAPI on FNGEN'

    return api
