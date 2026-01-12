# app/cli.py
import click

from app.seeders.db_seed import run


def register_commands(app):
    @app.cli.command("db:seed")
    def seed():
        run()
        click.echo("Database seeded successfully")
