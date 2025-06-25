from typing import Any, Callable, Self, cast
import os

from nicegui import ui
from nicegui.element import Element
from nicegui.events import GenericEventArguments
from nicegui.binding import BindableProperty, bind_to, bind_from, bind


class PdfViewer(Element, component="pdf_viewer.js"):

    current_page = BindableProperty(
        on_change=lambda sender, current_page: cast(Self, sender)._on_page_change_in_py(
            current_page
        )
    )

    num_pages = BindableProperty()
    is_rendering = BindableProperty()
    selected_text = BindableProperty()

    def __init__(self, path: str) -> None:
        super().__init__()
        self._props["path"] = path
        self.current_page = 1
        self.num_pages = 0
        self.is_rendering = False
        self.selected_text = ""

        self.on("change_current_page", self._on_page_change_in_js)
        self.on("change_num_pages", self._on_number_pages_change_in_js)
        self.on("change_is_rendering", self._on_is_rendering_change_in_js)
        self.on("change_selected_text", self._on_selected_text_change_in_js)

        # Load pdf_viewer.min.css from same path as this file
        self._load_css_file("pdf_viewer.min.css")
        self._load_js_file("pdf.min.js")
        self._load_js_file("jquery.min.js")
        self._load_worker("pdf.worker.min.js")

    #
    # General functions
    #
    def refresh(self) -> Self:
        """Refresh the PDF viewer."""
        self.run_method("refresh")
        return self

    #
    # Bindables
    #
    def bind_current_page(
        self,
        target_object: Any,
        target_name: str = "current_page",
        forward: Callable[..., Any] = lambda x: x,
        backward: Callable[..., Any] = lambda x: x,
    ) -> Self:
        bind(
            self,
            "current_page",
            target_object,
            target_name,
            forward=forward,
            backward=backward,
        )
        return self

    def bind_current_page_to(
        self,
        target_object: Any,
        target_name: str = "current_page",
        forward: Callable[..., Any] = lambda x: x,
    ) -> Self:
        bind_to(self, "current_page", target_object, target_name, forward)
        return self

    def bind_current_page_from(
        self,
        target_object: Any,
        target_name: str = "current_page",
        backward: Callable[..., Any] = lambda x: x,
    ) -> Self:
        bind_from(self, "current_page", target_object, target_name, backward)
        return self

    def bind_num_pages_to(
        self,
        target_object: Any,
        target_name: str = "num_pages",
        forward: Callable[..., Any] = lambda x: x,
    ) -> Self:
        bind_to(self, "num_pages", target_object, target_name, forward)
        return self

    def bind_is_rendering_to(
        self,
        target_object: Any,
        target_name: str = "is_rendering",
        forward: Callable[..., Any] = lambda x: x,
    ) -> Self:
        bind_to(self, "is_rendering", target_object, target_name, forward)
        return self

    def bind_selected_text_to(
        self,
        target_object: Any,
        target_name: str = "selected_text",
        forward: Callable[..., Any] = lambda x: x,
    ) -> Self:
        bind_to(self, "selected_text", target_object, target_name, forward)
        return self

    #
    # Events and binding
    #
    def _handle_current_page_change(self, text: str) -> None:
        """Called when the text of this element changes.

        :param text: The new text.
        """
        self._text_to_model_text(text)
        self.update()

    def _text_to_model_text(self, text: str) -> None:
        self._text = text

    def _on_page_change_in_py(self, e: int):
        self.run_method("open_page", e)

    def _on_page_change_in_js(self, e: GenericEventArguments):
        if self.current_page == e.args:
            return

        self.current_page = e.args

    def _on_number_pages_change_in_js(self, e: GenericEventArguments):
        if self.num_pages == e.args:
            return

        self.num_pages = e.args

    def _on_is_rendering_change_in_js(self, e: GenericEventArguments):
        if self.is_rendering == e.args:
            return

        self.is_rendering = e.args

    def _on_selected_text_change_in_js(self, e: GenericEventArguments):
        if self.selected_text == e.args:
            return

        self.selected_text = e.args

    #
    # Helper for pdf.js library
    #
    def _load_worker(self, resource: str) -> None:
        # Load the worker from the same path as this file
        resource_path = os.path.join(os.path.dirname(__file__), "pdf_js", resource)
        with open(resource_path, "r") as f:
            workerjs = f.read()

        js_content = f"""
            var PDFJS = window['pdfjs-dist/build/pdf'];
            PDFJS.GlobalWorkerOptions.workerSrc = {workerjs};
        """
        ui.add_body_html(f"\n<script>\n{js_content}\n</script>\n")

    def _load_css_file(self, resource: str):
        css_content = self._load_lib_file(resource)
        ui.add_body_html(f"\n<style>\n{css_content}\n</style>\n")

    def _load_js_file(self, resource: str):
        js_content = self._load_lib_file(resource)
        ui.add_body_html(f"\n<script>\n{js_content}\n</script>\n")

    def _load_lib_file(self, resource: str) -> str:
        # Load the resource from the same path as this file
        resource_path = os.path.join(os.path.dirname(__file__), "pdf_js", resource)
        with open(resource_path, "r") as f:
            return f.read()
