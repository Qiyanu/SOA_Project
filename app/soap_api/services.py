from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Client

class UserAuthService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=Unicode)
    def register_user(ctx, username, password):
        """
        Register a new user.
        """
        db: Session = SessionLocal()

        # Check if the username already exists
        existing_user = db.query(Client).filter(Client.username == username).first()
        if existing_user:
            return "Error: Username already exists."

        # Register the new user
        new_user = Client(username=username, password=password)
        db.add(new_user)
        db.commit()
        db.close()

        return "User registered successfully."

    @rpc(Unicode, Unicode, _returns=Unicode)
    def authenticate_user(ctx, username, password):
        """
        Authenticate a user.
        """
        db: Session = SessionLocal()

        # Check credentials
        user = db.query(Client).filter(Client.username == username, Client.password == password).first()
        db.close()

        if user:
            return f"Authentication successful for user: {username}"
        else:
            return "Error: Invalid username or password."

# Spyne Application
user_auth_app = Application(
    [UserAuthService],
    tns="soap.user.auth",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)

# WSGI Application
wsgi_app = WsgiApplication(user_auth_app)
