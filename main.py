from deta import App
from api.main import app
from src.utils import clear_deta_cache


app = App(app)

@app.lib.cron()
def cron_job(event):
	clear_deta_cache()
	return "Job completed"