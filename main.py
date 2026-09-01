import json
import flet as ft

COLOR_MAP = {
    "ВП": "#FF0000", "ТП": "#00B050", "ТДД": "#00B0F0", "ФП": "#C00000",
    "НПП": "#92D050", "ПП": "#FFFF00", "СП": "#E0E0E0", "ПІДГОТОВКА": "#00FF00"
}

class MilitaryMobileApp:
    def __init__(self):
        self.json_data = None
        self.current_items = []
        self.selected_item_index = None
        
        self.embedded_json = {
            "templates": [
                {
                    "name": "6 НР 2 НБ (Мобільний)",
                    "templateItems": [
                        {"id": 1, "dayNum": 1, "startTime": "08:30:00", "endTime": "10:00:00", "chapter": "Індивідуальна", "subject": "Вогнева підготовка", "abbr": "ВП 1/5", "classType": "(П)", "location": "Тир"},
                        {"id": 2, "dayNum": 1, "startTime": "10:15:00", "endTime": "11:45:00", "chapter": "Індивідуальна", "subject": "Тактична підготовка", "abbr": "ТП 5/1", "classType": "(П)", "location": "Поле"},
                        {"id": 3, "dayNum": 2, "startTime": "08:30:00", "endTime": "10:00:00", "chapter": "Індивідуальна", "subject": "Тактико-спеціальна", "abbr": "ТДД 1/6", "classType": "(П)", "location": "Зв'язок"}
                    ]
                }
            ],
            "algorithms": []
        }

    def build_main_ui(self, page: ft.Page):
        self.page = page
        self.page.title = "Менеджер БЗВП Мобільний"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.scroll = ft.ScrollMode.ADAPTIVE
        
        self.grid_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=10, expand=True)
        
        self.source_dropdown = ft.Dropdown(
            label="Категорія", width=180, corner_radius=8,
            options=[ft.dropdown.Option("templates", "Шаблони"), ft.dropdown.Option("algorithms", "Алгоритми")],
            on_change=self.on_source_changed, value="templates"
        )
        self.filter_dropdown = ft.Dropdown(label="Підрозділ / Взвод", expand=True, corner_radius=8, on_change=self.on_filter_changed)

        self.page.add(
            ft.AppBar(title=ft.Text("Розклад занять БЗВП"), center_title=True, bg_color="#1A1C1A"),
            ft.Row([
                ft.ElevatedButton("📁 JSON", icon=ft.icons.FOLDER_OPEN, on_click=lambda _: self.pick_file_dialog.pick_files()),
                ft.ElevatedButton("📤 Експорт", icon=ft.icons.SAVE, on_click=self.export_json_file)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.source_dropdown, self.filter_dropdown]),
            ft.Divider(),
            self.grid_row
        )

        self.pick_file_dialog = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(self.pick_file_dialog)
        
        self.json_data = self.embedded_json
        self.update_filter_dropdown("templates")

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if not e.files: return
        try:
            with open(e.files[path], "r", encoding="utf-8") as f:
                self.json_data = json.load(f)
            self.update_filter_dropdown("templates")
        except:
            pass

    def on_source_changed(self, e):
        self.update_filter_dropdown(self.source_dropdown.value)

    def update_filter_dropdown(self, key):
        if key in self.json_data:
            self.filter_dropdown.options = [ft.dropdown.Option(item["name"]) for item in self.json_data[key]]
            if self.json_data[key]:
                self.filter_dropdown.value = self.json_data[key]["name"]
                self.render_calendar_grid(self.filter_dropdown.value)
            self.page.update()

    def on_filter_changed(self, e):
        self.render_calendar_grid(self.filter_dropdown.value)
    def render_calendar_grid(self, selected_name):
        self.grid_row.controls.clear()
        source_type = self.source_dropdown.value
        target_group = next((g for g in self.json_data.get(source_type, []) if g["name"] == selected_name), None)
        if not target_group: return

        item_key = "templateItems" if source_type == "templates" else "algorithmItems"
        self.current_items = target_group.get(item_key, [])

        days_data = {}
        for idx, item in enumerate(self.current_items):
            day_key = f"День {item.get('dayNum', 1)}" if source_type == "templates" else str(item.get("date", "2026-09-01"))
            if day_key not in days_data: days_data[day_key] = []
            days_data[day_key].append((idx, item))

        for day_title, items_list in sorted(days_data.items()):
            day_column = ft.Column(width=190, scroll=ft.ScrollMode.ADAPTIVE)
            day_container = ft.Container(content=day_column, bgcolor="#1E201E", border_radius=10, padding=8, border=ft.border.all(1, "#333633"))
            day_column.controls.append(ft.Container(content=ft.Text(day_title, weight="bold", size=13), alignment=ft.alignment.center, padding=5))

            for global_idx, item in items_list:
                subj = item.get("subject", "")
                abbr = item.get("abbr", "")
                card_color = "#454545"
                for key, code in COLOR_MAP.items():
                    if key.lower() in subj.lower() or key.lower() in abbr.lower(): card_color = code; break
                text_color = "black" if card_color in ["#FFFF00", "#92D050", "#E0E0E0", "#00FF00"] else "white"

                card = ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text(item.get("startTime", "")[:5], size=10, color=text_color, weight="bold")]),
                        ft.Text(f"{subj} {abbr}".strip(), size=11, weight="bold", color=text_color, text_align=ft.TextAlign.CENTER),
                        ft.Row([
                            ft.IconButton(ft.icons.EDIT, icon_size=14, icon_color=text_color, on_click=lambda _, idx=global_idx: self.open_mobile_modal(idx)),
                            ft.IconButton(ft.icons.DELETE, icon_size=14, icon_color="#FF4d4d", on_click=lambda _, idx=global_idx: self.delete_mobile_item(idx))
                        ], alignment=ft.MainAxisAlignment.END, spacing=0)
                    ], spacing=2, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=card_color, border_radius=8, padding=6, height=95, width=175
                )
                day_column.controls.append(card)
            self.grid_row.controls.append(day_container)
        self.page.update()
    def open_mobile_modal(self, index):
        self.selected_item_index = index
        item_data = self.current_items[index]
        
        self.input_fields = {
            "startTime": ft.TextField(label="Час початку", value=item_data.get("startTime", "")),
            "endTime": ft.TextField(label="Час закінчення", value=item_data.get("endTime", "")),
            "subject": ft.TextField(label="Предмет підготовки", value=item_data.get("subject", "")),
            "abbr": ft.TextField(label="Абревіатура", value=item_data.get("abbr", "")),
            "topic": ft.TextField(label="Тема / Заняття", value=item_data.get("topic", ""), multiline=True, min_lines=2),
            "location": ft.TextField(label="Локація / Місце", value=item_data.get("location", ""))
        }

        self.modal_dialog = ft.AlertDialog(
            title=ft.Text("Редагування заняття", size=16, weight="bold"),
            content=ft.Column(list(self.input_fields.values()), tight=True, scroll=ft.ScrollMode.ADAPTIVE, width=320),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda _: self.close_modal()),
                ft.ElevatedButton("Зберегти", bgcolor="#007bff", color="white", on_click=self.save_mobile_modal_data)
            ]
        )
        self.page.dialog = self.modal_dialog
        self.modal_dialog.open = True
        self.page.update()

    def save_mobile_modal_data(self, e):
        item_data = self.current_items[self.selected_item_index]
        for key, field in self.input_fields.items():
            item_data[key] = field.value
        self.close_modal()
        self.render_calendar_grid(self.filter_dropdown.value)

    def close_modal(self):
        self.modal_dialog.open = False
        self.page.update()

    def delete_mobile_item(self, index):
        self.current_items.pop(index)
        self.render_calendar_grid(self.filter_dropdown.value)

    def export_json_file(self, e):
        print(json.dumps(self.json_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    app_instance = MilitaryMobileApp()
    ft.app(target=app_instance.build_main_ui)
