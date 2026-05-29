import click

@click.group()
@click.option("--context", default="default", help="Proyecto o cuenta activa")
@click.option("--debug", is_flag=True, help="Activa salida de depuración")
@click.option("--endpoint", default="https://api.go.develeopers.ai/v1", help="Endpoint de la API")
@click.pass_context
def cli(ctx, context, debug, endpoint):
    ctx.obj = {"context": context, "debug": debug, "endpoint": endpoint}

@cli.command()
def servers():
    """Lista servidores activos"""
    click.echo("[srv-001] Bot Engine - Running")
    click.echo("[srv-002] Dashboard - Stopped")

@cli.command()
@click.argument("app_name")
def deploy(app_name):
    """Despliega aplicación"""
    click.echo(f"✔ Deploy completado para {app_name}")

@cli.command()
def affiliates():
    """Muestra módulos de afiliados activos"""
    click.echo("Afiliados activos: Stripe, PayPal, OpenPay")

@cli.command()
def payments():
    """Consulta pagos registrados"""
    click.echo("Pagos: u001 - $10.5 (Stripe), u002 - $25.0 (PayPal)")

if __name__ == "__main__":
    cli()
