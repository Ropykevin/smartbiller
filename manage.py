from app import create_app, db
from flask_migrate import Migrate
from flask.cli import with_appcontext
import click

app = create_app()
migrate = Migrate(app, db)

@app.cli.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    click.echo("Database initialized.")
