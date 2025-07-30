import click

@click.command()
@click.option('--source', prompt='Source path', help='Path to the content source')
@click.option('--dest', prompt='Destination path', help='Path to the destination')
def ingest(source, dest):
    """Ingest content from source to destination."""
    click.echo(f"Ingesting from {source} to {dest}")

if __name__ == "__main__":
    ingest()