import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://constructiq:constructiq@db:5432/constructiq")

TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL
    },
    "apps": {
        "models": {
            "models": [
                "app.models.geography",
                "app.models.company",
                "app.models.project",
                "app.models.user",
                "app.models.document",
                "app.models.asset",
                "app.models.commissioning",
                "app.models.billing",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    }
}
