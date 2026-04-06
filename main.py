import flet as ft
from models import Stage, STAGE_LABELS, STAGE_COLORS
from store import load_candidates, save_candidates, add_candidate, update_candidate_stage, delete_candidate
from components import candidate_card, add_candidate_dialog, candidate_detail_dialog


def main(page: ft.Page):
    page.title = "Hiring Pipeline"
    page.bgcolor = "#F9FAFB"
    page.padding = 0
    page.window.width = 960
    page.window.height = 700
    page.fonts = {"Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"}
    page.theme = ft.Theme(font_family="Inter")

    candidates = load_candidates()
    current_filter = {"stage": None}  # None = all

    cards_grid = ft.GridView(
        expand=True,
        runs_count=3,
        max_extent=300,
        child_aspect_ratio=1.6,
        spacing=16,
        run_spacing=16,
        padding=24,
    )

    count_text = ft.Text("", size=13, color="#9CA3AF")

    def refresh_cards():
        cards_grid.controls.clear()
        filtered = candidates if current_filter["stage"] is None else [
            c for c in candidates if c.stage == current_filter["stage"]
        ]
        count_text.value = f"{len(filtered)} candidate{'s' if len(filtered) != 1 else ''}"
        for c in filtered:
            cards_grid.controls.append(candidate_card(c, on_card_click))
        page.update()

    def on_card_click(candidate):
        def handle_advance(c):
            next_s = c.next_stage()
            if next_s:
                update_candidate_stage(candidates, c.id, next_s)
            detail_dlg.open = False
            refresh_cards()

        def handle_reject(c):
            update_candidate_stage(candidates, c.id, Stage.REJECTED)
            detail_dlg.open = False
            refresh_cards()

        def handle_delete(c):
            delete_candidate(candidates, c.id)
            detail_dlg.open = False
            refresh_cards()

        detail_dlg = candidate_detail_dialog(page, candidate, handle_advance, handle_reject, handle_delete)
        page.overlay.append(detail_dlg)
        detail_dlg.open = True
        page.update()

    def on_add_save(name, role):
        add_candidate(candidates, name, role)
        refresh_cards()

    add_dlg = add_candidate_dialog(page, on_add_save)
    page.overlay.append(add_dlg)

    def open_add_dialog(e):
        add_dlg.open = True
        page.update()

    # Sidebar filter buttons
    def make_filter_btn(label, stage_value):
        is_all = stage_value is None
        count = len(candidates) if is_all else len([c for c in candidates if c.stage == stage_value])

        def on_filter(e):
            current_filter["stage"] = stage_value
            rebuild_sidebar()
            refresh_cards()

        active = current_filter["stage"] == stage_value
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=("#111827" if is_all else STAGE_COLORS.get(stage_value, "#111827")) if active else "transparent",
                    ),
                    ft.Text(
                        label,
                        size=13,
                        weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                        color="#111827" if active else "#6B7280",
                        expand=True,
                    ),
                    ft.Text(str(count), size=12, color="#9CA3AF"),
                ],
                spacing=8,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=8,
            bgcolor="#F3F4F6" if active else "transparent",
            on_click=on_filter,
            ink=True,
        )

    sidebar_filters = ft.Column(spacing=2)

    def rebuild_sidebar():
        sidebar_filters.controls.clear()
        sidebar_filters.controls.append(make_filter_btn("All Candidates", None))
        for stage in [Stage.APPLIED, Stage.INTERVIEW, Stage.OFFER, Stage.HIRED, Stage.REJECTED]:
            sidebar_filters.controls.append(make_filter_btn(STAGE_LABELS[stage], stage))

    rebuild_sidebar()

    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Text("Pipeline", size=11, weight=ft.FontWeight.W_600, color="#9CA3AF"),
                    padding=ft.padding.only(left=16, top=8, bottom=4),
                ),
                sidebar_filters,
            ],
            spacing=4,
        ),
        width=200,
        bgcolor="white",
        border=ft.border.only(right=ft.BorderSide(1, "#E5E7EB")),
        padding=ft.padding.only(top=16, bottom=16),
    )

    top_bar = ft.Container(
        content=ft.Row(
            [
                ft.Text("Hiring", size=20, weight=ft.FontWeight.W_700, color="#111827"),
                count_text,
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Add Candidate",
                    icon=ft.Icons.ADD,
                    on_click=open_add_dialog,
                    bgcolor="#111827",
                    color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, "#E5E7EB")),
    )

    main_content = ft.Column(
        [top_bar, cards_grid],
        expand=True,
        spacing=0,
    )

    page.add(
        ft.Row(
            [sidebar, main_content],
            expand=True,
            spacing=0,
        )
    )

    refresh_cards()


ft.app(target=main)
