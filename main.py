# main.py 
from flask import jsonify
from api.app import create_app

app = create_app()


@app.cli.group()
def db():
    """Database commands."""
    pass

@db.command()
def upgrade():
  """Create or upgrade the database."""
  from alembic.config import main
  main(argv=['upgrade', 'head'])

@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify(message="Hello, World!")
