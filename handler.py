from mangum import Mangum

from core.main import app

handler = Mangum(app)  # pragma: no cover
