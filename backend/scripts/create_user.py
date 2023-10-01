from perry.db.session import DatabaseSessionManager as DSM
from perry.db.operations.users import create_user
import click


@click.command()
@click.argument("username", type=str)
@click.argument("password", type=str)
def create_new_user(username, password):
    click.echo(f"Creating user {username}")
    db_session = DSM.get_db_session()
    create_user(db_session, username, password)
    click.echo(f"User {username} created.")

if __name__ == "__main__":
    create_new_user()