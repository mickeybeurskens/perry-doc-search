import click
import requests


@click.command()
@click.argument("username", type=str)
@click.argument("password", type=str)
def create_new_user(username, password):
    click.echo(f"Creating user {username}")
    response = requests.post(
        "http://localhost:8000/users/register", json={"username": username, "password": password}
    )
    if response.status_code != 200:
        click.echo(f"Failed to create user {username}.")
        click.echo(response.json())
        return
    click.echo(f"User {username} created.")

if __name__ == "__main__":
    create_new_user()