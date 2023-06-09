def deploy():
    """Run deployment tasks."""
    from app import create_app, db
    from flask_migrate import upgrade, migrate, init, stamp
    from filemate.grades_db import User

    app = create_app()
    app.app_context().push()
    db.create_all()

    # migrate database to latest revision
    stamp()
    migrate()
    upgrade()


deploy()