import flet as ft
from models import Candidate, Stage, STAGE_LABELS, STAGE_COLORS


def stage_badge(stage: Stage) -> ft.Container:
    return ft.Container(
        content=ft.Text(STAGE_LABELS[stage], size=11, weight=ft.FontWeight.W_600, color="white"),
        bgcolor=STAGE_COLORS[stage],
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )


def candidate_card(candidate: Candidate, on_click) -> ft.Container:
    initials = "".join(w[0].upper() for w in candidate.name.split()[:2])

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(initials, size=14, weight=ft.FontWeight.W_600, color="#6B7280"),
                            width=40,
                            height=40,
                            border_radius=20,
                            bgcolor="#F3F4F6",
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            [
                                ft.Text(candidate.name, size=14, weight=ft.FontWeight.W_600, color="#111827"),
                                ft.Text(candidate.role, size=12, color="#6B7280"),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Row([stage_badge(candidate.stage)]),
            ],
            spacing=12,
        ),
        padding=20,
        border_radius=12,
        bgcolor="white",
        border=ft.border.all(1, "#E5E7EB"),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.06, "black"),
            offset=ft.Offset(0, 2),
        ),
        on_click=lambda e: on_click(candidate),
        ink=True,
        width=280,
    )


def add_candidate_dialog(page: ft.Page, on_save) -> ft.AlertDialog:
    name_field = ft.TextField(label="Full Name", autofocus=True, border_radius=8)
    role_field = ft.TextField(label="Role", border_radius=8)

    def handle_save(e):
        if name_field.value and role_field.value:
            on_save(name_field.value.strip(), role_field.value.strip())
            dialog.open = False
            name_field.value = ""
            role_field.value = ""
            page.update()

    def handle_cancel(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        title=ft.Text("Add Candidate", size=18, weight=ft.FontWeight.W_600),
        content=ft.Column([name_field, role_field], spacing=16, tight=True, width=320),
        actions=[
            ft.TextButton("Cancel", on_click=handle_cancel),
            ft.ElevatedButton(
                "Add",
                on_click=handle_save,
                bgcolor="#111827",
                color="white",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            ),
        ],
    )
    return dialog


def candidate_detail_dialog(page: ft.Page, candidate: Candidate, on_advance, on_reject, on_delete) -> ft.AlertDialog:
    from models import STAGE_ORDER

    next_stage = candidate.next_stage()
    actions = []

    if next_stage and candidate.stage != Stage.REJECTED:
        actions.append(
            ft.ElevatedButton(
                f"Move to {STAGE_LABELS[next_stage]}",
                on_click=lambda e: on_advance(candidate),
                bgcolor="#111827",
                color="white",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            )
        )

    if candidate.stage not in (Stage.REJECTED, Stage.HIRED):
        actions.append(
            ft.OutlinedButton(
                "Reject",
                on_click=lambda e: on_reject(candidate),
                style=ft.ButtonStyle(
                    color="#EF4444",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            )
        )

    actions.append(
        ft.TextButton(
            "Delete",
            on_click=lambda e: on_delete(candidate),
            style=ft.ButtonStyle(color="#9CA3AF"),
        )
    )

    dialog = ft.AlertDialog(
        title=ft.Text(candidate.name, size=20, weight=ft.FontWeight.W_600),
        content=ft.Column(
            [
                ft.Text(candidate.role, size=14, color="#6B7280"),
                ft.Container(height=8),
                ft.Row([ft.Text("Status:", size=13, color="#9CA3AF"), stage_badge(candidate.stage)], spacing=8),
            ],
            tight=True,
            spacing=8,
            width=320,
        ),
        actions=actions,
    )
    return dialog
