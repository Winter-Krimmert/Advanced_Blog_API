from flask import Flask
from flask_migrate import Migrate
from app import create_app, db  # Ensure these imports are correct

# Create an app instance using the factory function
app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
