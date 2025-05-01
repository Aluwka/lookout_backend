from .core.app.app_creator import app_creator


app = app_creator.create_app()
app_creator.add_templates()
app_creator.mount_static()

