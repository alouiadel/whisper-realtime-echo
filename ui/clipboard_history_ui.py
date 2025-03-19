"""UI components for clipboard history."""
import flet as ft
import datetime
from logic.clipboard_history import ClipboardHistory
from ui.theme_lang import AppThemeLang
import threading

def create_history_dialog(page: ft.Page, clipboard_history: ClipboardHistory, on_copy: callable):
    """Create a dialog for viewing and interacting with clipboard history.
    
    Args:
        page: The Flet page
        clipboard_history: The clipboard history manager
        on_copy: Callback for when an item is copied
        
    Returns:
        Dialog component
    """
    dialog = ft.AlertDialog(
        title=ft.Text("Clipboard History", size=20, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                ft.Text(
                    "Only the most recent 50 entries are retained",
                    size=12,
                    italic=True,
                    color=ft.colors.GREY_600,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        height=400,
                        width=600,
                    ),
                    padding=10,
                ),
            ],
            tight=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Clear History", on_click=lambda _: clear_history()),
            ft.TextButton("Close", on_click=lambda _: close_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def create_history_item(item):
        """Create a single history item card."""
        try:
            timestamp = datetime.datetime.fromisoformat(item["timestamp"])
            date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, KeyError, TypeError):
            date_str = "Unknown date"
            
        item_success_text = ft.Text(
            "✓ Copied!",
            color=AppThemeLang.SUCCESS_COLOR,
            weight=ft.FontWeight.BOLD,
            visible=False,
            size=14,
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(date_str, size=12, color=ft.colors.GREY_500),
                        ft.Text(
                            item.get("model_name", ""),
                            size=12, 
                            color=AppThemeLang.SECONDARY_COLOR, 
                            italic=True
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=1, color=ft.colors.GREY_300),
                    ft.Text(
                        item["text"], 
                        size=14, 
                        selectable=True,
                        max_lines=3,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Row([
                        item_success_text,
                        ft.ElevatedButton(
                            "Copy",
                            icon=ft.icons.CONTENT_COPY,
                            on_click=lambda _, text=item["text"], msg=item_success_text: copy_item(text, msg),
                            style=ft.ButtonStyle(
                                color=ft.colors.WHITE,
                                bgcolor=AppThemeLang.PRIMARY_COLOR,
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.END, spacing=10),
                ]),
                padding=10,
            ),
            elevation=1,
            margin=ft.margin.only(bottom=10),
        )
    
    def refresh_history():
        """Refresh the history display."""
        history_items = clipboard_history.get_history()
        list_container = dialog.content.controls[1].content
        
        if not history_items:
            list_container.controls = [
                ft.Text("No history items found", italic=True, color=ft.colors.GREY_500)
            ]
        else:
            list_container.controls = [
                create_history_item(item) for item in history_items
            ]
        
        page.update()
    
    def copy_item(text, success_msg):
        """Copy a history item to the clipboard."""
        page.set_clipboard(text)
        
        success_msg.visible = True
        dialog.update()
        
        threading.Timer(2.0, lambda msg=success_msg: hide_success_message(msg)).start()
    
    def hide_success_message(msg):
        """Hide the success message."""
        msg.visible = False
        dialog.update()
    
    def clear_history():
        """Clear all history items."""
        clipboard_history.clear_history()
        refresh_history()
    
    def close_dialog():
        """Close the dialog."""
        page.dialog.open = False
        page.update()
    
    def open_dialog():
        """Open the dialog."""
        refresh_history()
        page.dialog = dialog
        page.dialog.open = True
        page.update()
    
    return dialog, open_dialog 