import flet as ft
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# general variables
app_name = "pyLab Manager"


# SQLAlchemy setup
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(Text)

# Database connection and session setup
DATABASE_URL = "sqlite:///inventory.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Database setup
def setup_database():
    Base.metadata.create_all(engine)  # Create tables
    if not session.query(User).filter_by(username="admin").first():
        admin = User(username="admin", password="fer",email="fer.muzzo@gmail.com")
        session.add(admin)
        session.commit()

# Validate user login
def validate_user(username, password):
    return session.query(User).filter_by(username=username, password=password).first() is not None


# Add an item to the inventory
def add_item_to_inventory(name, quantity, description):
    new_item = InventoryItem(name=name, quantity=quantity, description=description)
    session.add(new_item)
    session.commit()

# Search items in the inventory
def search_items_in_inventory(search_term):
    return session.query(InventoryItem).filter(InventoryItem.name.like(f"%{search_term}%")).all()

# Main application
def main(page: ft.Page):
    page.title = "Inventory Manager"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 800
    page.window_height = 600

    authenticated_user = None  # Track authenticated user

    # Navigation Functions
    def load_main_view():
        """Load the main view after successful login."""
        page.views.clear()
        page.views.append(main_view())
        page.update()

    def logout_user(e):
        """Logout user and return to the login page."""
        nonlocal authenticated_user
        authenticated_user = None  # Reset the authenticated user
        page.views.clear()
        page.views.append(login_view())  # Redirect to the login page
        page.update()

    # Login View
    def login_view():
    
        username_field = ft.TextField(label="Username", autofocus=True, expand=True)
        password_field = ft.TextField(label="Password", password=True, expand=True)

        new_username_field = ft.TextField(label="Username", autofocus=True, expand=True)
        new_password_field = ft.TextField(label="Password", password=True, expand=True)
        new_email_field = ft.TextField(label="email", autofocus=True, expand=True)
        error_text = ft.Text(color=ft.colors.RED)


        def handle_login(e):
            nonlocal authenticated_user
            if validate_user(username_field.value, password_field.value):
                authenticated_user = username_field.value  # Track logged-in user
                load_main_view()
            else:
                error_text.color=ft.colors.RED
                error_text.value = "Invalid username or password. Please try again."
                error_text.update()
        
        def create_new_admin(e):

            def handle_close(e):
                page.close(dlg_modal)

            def create_admin(e):
                if (not session.query(User).filter_by(username=new_username_field.value).first()) or (not session.query(User).filter_by(email=new_email_field.value).first()):
                    admin = User(username=new_username_field.value, password=new_password_field.value,email=new_email_field.value)
                    session.add(admin)
                    session.commit()
                    page.close(dlg_modal)
                    error_text.color=ft.colors.GREEN
                    error_text.value = "New lab and admin user created."
                    error_text.update()
                else:
                    page.close(dlg_modal)
                    error_text.color=ft.colors.RED
                    error_text.value = "email or user name already exist."
                    error_text.update()


            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Setting up lab..."),
                content=ft.Column([ft.Text("Create a new admin user"),
                                   new_username_field,
                                   new_password_field,
                                   new_email_field]),
                actions=[
                    ft.TextButton("Create", on_click=create_admin),
                    ft.TextButton("Cancel", on_click=handle_close),
                ],
                actions_alignment=ft.MainAxisAlignment.END,

            )

            page.open(dlg_modal)


        return ft.View(
            controls=[ft.Row([ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Login to Inventory Manager", size=24),
                        username_field,
                        password_field,
                        ft.Row([ft.FilledButton("Login", on_click=handle_login),
                                ft.TextButton("Create new lab", on_click=create_new_admin)],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        error_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=350,
                height=250,
            )],
            alignment=ft.MainAxisAlignment.CENTER)
            ]
        )

    # Main View with Navigation Bar
    def main_view():

        def switch_to_view(view_function):
            """Switch to a different view in the main interface."""
            main_container.controls.clear()
            main_container.controls.append(view_function())
            main_container.update()
        
        def inventory_view():
            search_results = ft.Column()

            def search_items(e):
                search_term = search_field.value
                items = search_items_in_inventory(search_term)
                search_results.controls.clear()
                if items:
                    for item in items:
                        search_results.controls.append(
                            ft.Text(f"ID: {item.id}, Name: {item.name}, Quantity: {item.quantity}, Description: {item.description}")
                        )
                else:
                    search_results.controls.append(ft.Text("No items found."))
                search_results.update()

            search_field = ft.TextField(label="Buscar items", expand=True)
            return ft.Column(
                [
                    ft.Text("Search Inventory", size=20),
                    ft.Row([search_field, ft.ElevatedButton("Search", on_click=search_items)]),
                    search_results,
                ],
                scroll=ft.ScrollMode.AUTO,
            )

        def add_item_view():
            def add_item(e):
                add_item_to_inventory(
                    name_field.value,
                    int(quantity_field.value),
                    description_field.value,
                )
                name_field.value = ""
                quantity_field.value = ""
                description_field.value = ""
                name_field.update()
                quantity_field.update()
                description_field.update()

            name_field = ft.TextField(label="Item name", expand=True)
            quantity_field = ft.TextField(label="Quantity", expand=True, keyboard_type=ft.KeyboardType.NUMBER)
            description_field = ft.TextField(label="Description", expand=True)

            return ft.Column(
                [
                    ft.Text("Add New Item", size=20),
                    name_field,
                    quantity_field,
                    description_field,
                    ft.ElevatedButton("Add Item", on_click=add_item),
                ],
                scroll=ft.ScrollMode.AUTO,
            )

        def toggle_theme(e):
            # Switch between dark and light themes
            page.theme_mode = (
                ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
            )
            page.update()

        # Navigation Bar
        def navigation_bar():
            return ft.AppBar(
                leading=ft.Icon(ft.icons.MORE_HORIZ_ROUNDED),
                leading_width=40,
                title=ft.Text(app_name),
                center_title=False,
                bgcolor=ft.colors.SURFACE_VARIANT,
                actions=[
                    ft.IconButton(ft.icons.LIGHT_MODE, on_click=toggle_theme),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(text="Settings"),
                            ft.PopupMenuItem(),  # divider
                            ft.PopupMenuItem(text="Log out", icon = ft.icons.EXIT_TO_APP, on_click=logout_user),
                        ],
                        icon = ft.icons.EXIT_TO_APP,
                    ),
                ],
            )
        
        # Side panel
        def side_panel():
            return ft.Row(
                [
                    ft.ElevatedButton("Search Inventory", on_click=lambda e: switch_to_view(inventory_view)),
                    ft.ElevatedButton("Add Item", on_click=lambda e: switch_to_view(add_item_view)),
                    ft.ElevatedButton("Logout", on_click=logout_user, bgcolor=ft.colors.RED),  # Logout button
                ],
                alignment=ft.MainAxisAlignment.START,
            )

        # Main Container
        main_container = ft.Column([inventory_view()], expand=True)

        return ft.View(
            controls=[
                navigation_bar(),
                main_container,
            ]
        )

    # Load login view initially
    page.views.append(login_view())
    page.update()


if __name__ == "__main__":
    setup_database()
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
