import json
import flet as ft
from datetime import datetime, timedelta

COLOR_MAP = {
    "ВП": "#D32F2F", "ТП": "#2E7D32", "ТДД": "#1565C0", "ФП": "#C62828",
    "НПП": "#689F38", "ПП": "#FBC02D", "СП": "#757575", "ПІДГОТОВКА": "#4CAF50"
}

DAYS_ORDER = {
    "понеділок": 1, "вівторок": 2, "середа": 3, "четвер": 4, 
    "п'ятниця": 5, "субота": 6, "неділя": 7
}

class MilitaryMobileApp:
    def __init__(self):
        self.json_data = None
        self.current_items = []
        self.selected_item_index = None
        
        self.embedded_json = {
            "templates": [
                {
                    "name": "1 Рота 1 Взвод (Зразок)",
                    "templateItems": [
                        {"id": 1, "dayNum": 1, "startTime": "08:30:00", "endTime": "10:00:00", "chapter": "БЗВП", "subject": "Вогнева підготовка", "abbr": "ВП 1/5", "classType": "(П)", "location": "Тир", "hours": 2, "topic": "", "notes": ""},
                        {"id": 2, "dayNum": 1, "startTime": "10:15:00", "endTime": "11:45:00", "chapter": "БЗВП", "subject": "Тактична підготовка", "abbr": "ТП 3/1", "classType": "(П)", "location": "Поле", "hours": 2, "topic": "", "notes": ""}
                    ]
                }
            ],
            "algorithms": []
        }

    def build_main_ui(self, page: ft.Page):
        self.page = page
        self.page.title = "Менеджер БЗВП — Повний Екран Рот"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 10
        
        self.grid_scroll_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=15, expand=True)
        
        self.source_dropdown = ft.Dropdown(
            label="Категорія даних", width=140, on_change=self.on_source_changed, value="templates",
            options=[ft.dropdown.Option("templates", "Шаблони"), ft.dropdown.Option("algorithms", "Алгоритми")]
        )
        self.filter_dropdown = ft.Dropdown(label="Вибір Роти / Взводу", expand=True, on_change=self.on_filter_changed)

        self.page.add(
            ft.Row([
                ft.ElevatedButton("📁 JSON", icon=ft.icons.FOLDER_OPEN, on_click=lambda _: self.pick_file_dialog.pick_files()),
                ft.ElevatedButton("📅 Тиждень", icon=ft.icons.DATE_RANGE, on_click=self.open_generate_week_modal),
                ft.ElevatedButton("📤 Експорт", icon=ft.icons.SAVE, on_click=self.export_json_file)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.source_dropdown, self.filter_dropdown]),
            ft.Divider(),
            self.grid_scroll_row
        )

        self.pick_file_dialog = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(self.pick_file_dialog)
        self.json_data = self.embedded_json
        self.update_filter_dropdown("templates")
    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if not e.files or not e.files.path: return
        try:
            with open(e.files.path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
            
            if "templates" in parsed_data or "algorithms" in parsed_data:
                self.json_data = parsed_data
                self.source_dropdown.value = "templates"
                self.update_filter_dropdown("templates")
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Розклад успішно завантажено!"), open=True))
            else:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Помилка структури розкладу у вашому JSON файлі!"), open=True))
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Помилка імпорту розкладу: {str(ex)}"), open=True))

    def on_source_changed(self, e):
        self.update_filter_dropdown(self.source_dropdown.value)

    def update_filter_dropdown(self, key):
        if key in self.json_data and self.json_data[key]:
            self.filter_dropdown.options = [ft.dropdown.Option(item["name"]) for item in self.json_data[key]]
            self.filter_dropdown.value = self.json_data[key]["name"]
            self.render_calendar_grid(self.filter_dropdown.value)
        else:
            self.filter_dropdown.options = []
            self.filter_dropdown.value = None
            self.grid_scroll_row.controls.clear()
        self.page.update()

    def on_filter_changed(self, e):
        self.render_calendar_grid(self.filter_dropdown.value)

    def get_day_sort_key(self, day_title):
        title_lower = str(day_title).lower()
        for key, order in DAYS_ORDER.items():
            if key in title_lower: return (0, order, title_lower)
        if "день" in title_lower:
            try:
                num = int(''.join(filter(str.isdigit, title_lower)))
                return (1, num, title_lower)
            except: return (1, 999, title_lower)
        return (2, 999, title_lower)
    def render_calendar_grid(self, selected_name):
        self.grid_scroll_row.controls.clear()
        if not selected_name:
            self.page.update()
            return
            
        source_type = self.source_dropdown.value
        target_group = next((g for g in self.json_data.get(source_type, []) if g["name"] == selected_name), None)
        if not target_group:
            self.page.update()
            return

        item_key = "templateItems" if source_type == "templates" else "algorithmItems"
        self.current_items = target_group.get(item_key, [])

        days_data = {}
        for idx, item in enumerate(self.current_items):
            day_key = f"День {item.get('dayNum', 1)}"
            if "date" in item and item["date"]:
                try:
                    dt = datetime.strptime(item["date"], "%Y-%m-%d")
                    ukr_days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
                    day_key = f"{item['date']} ({ukr_days[dt.weekday()]})"
                except: day_key = str(item["date"])
            
            if day_key not in days_data: days_data[day_key] = []
            days_data[day_key].append((idx, item))

        ukr_days_lower = ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"]
        current_day_name = ukr_days_lower[datetime.now().weekday()]
        current_date_str = datetime.now().strftime("%Y-%m-%d")

        sorted_days = sorted(days_data.items(), key=lambda x: self.get_day_sort_key(x))

        today_index = None
        for i, (day_title, _) in enumerate(sorted_days):
            title_lower = str(day_title).lower()
            if (current_day_name in title_lower) or (current_date_str in title_lower):
                today_index = i
                break

        if today_index is not None and today_index > 0:
            sorted_days = sorted_days[today_index:] + sorted_days[:today_index]

        for col_idx, (day_title, items_list) in enumerate(sorted_days):
            day_column = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
            
            title_lower = str(day_title).lower()
            is_today = (current_day_name in title_lower) or (current_date_str in title_lower)

            day_container = ft.Container(
                content=day_column, width=210, 
                bgcolor="#252825" if is_today else "#1E201E", 
                border_radius=10, padding=8,
                border=ft.border.all(2, "#00B050" if is_today else "#333633")
            )
            
            day_column.controls.append(
                ft.Container(
                    content=ft.Text(day_title + (" (СЬОГОДНІ)" if is_today else ""), weight="bold", size=13, color="white"),
                    alignment=ft.alignment.center, padding=4, 
                    bgcolor="#00B050" if is_today else "#2D302D", 
                    border_radius=6
                )
            )

            sorted_items = sorted(items_list, key=lambda x: x.get("startTime", "00:00:00"))
            total_hours = 0
            
            for global_idx, item in sorted_items:
                subj = item.get("subject", "")
                abbr = item.get("abbr", "")
                start_t = item.get("startTime", "")[:5] if item.get("startTime") else "00:00"
                end_t = item.get("endTime", "")[:5] if item.get("endTime") else "00:00"
                try: total_hours += int(item.get("hours", 2))
                except: total_hours += 2

                card_color = "#454545"
                for key, code in COLOR_MAP.items():
                    if key.lower() in subj.lower() or key.lower() in abbr.lower():
                        card_color = code
                        break
                text_color = "black" if card_color in ["#FFFF00", "#92D050", "#E0E0E0", "#00FF00"] else "white"

                card = ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text(f"{start_t} - {end_t}", size=11, color=text_color, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Text(f"{subj} {abbr}".strip(), size=12, weight="bold", color=text_color, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{item.get('classType','')} {item.get('location','')}".strip(), size=10, color=text_color),
                        ft.Row([
                            ft.IconButton(ft.icons.EDIT, icon_color=text_color, icon_size=16, on_click=lambda _, idx=global_idx: self.open_mobile_modal(idx)),
                            ft.IconButton(ft.icons.DELETE, icon_color="#FF4D4D", icon_size=16, on_click=lambda _, idx=global_idx: self.delete_mobile_item(idx))
                        ], alignment=ft.MainAxisAlignment.END, spacing=0)
                    ], spacing=3, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=card_color, border_radius=8, padding=6, height=115, width=195
                )
                day_column.controls.append(card)
            
            day_column.controls.append(ft.Container(content=ft.Text(f"{total_hours} годин", weight="bold", size=11, color="#A0A0A0"), alignment=ft.alignment.center, padding=5))
            self.grid_scroll_row.controls.append(day_container)
            
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
                ft.ElevatedButton("Зберегти", bgcolor="#2E7D32", color="white", on_click=self.save_mobile_modal_data)
            ]
        )
        self.page.dialog = self.modal_dialog
        self.modal_dialog.open = True
        self.page.update()

    def open_generate_week_modal(self, e):
        self.start_date_field = ft.TextField(label="Дата Понеділка (РРРР-ММ-ДД)", value=datetime.now().strftime("%Y-%m-%d"), width=280)
        self.gen_dialog = ft.AlertDialog(
            title=ft.Text("Генерація тижневого розкладу", size=15, weight="bold"),
            content=ft.Column([
                ft.Text("Автоматично розставить календарні дати та назви днів тижня на основі обраного циклічного шаблону.", size=12),
                self.start_date_field
            ], tight=True, width=300),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda _: self.close_gen_modal()),
                ft.ElevatedButton("Згенерувати", bgcolor="#1565C0", color="white", on_click=self.generate_week_schedule)
            ]
        )
        self.page.dialog = self.gen_dialog
        self.gen_dialog.open = True
        self.page.update()

    def generate_week_schedule(self, e):
        try: start_date = datetime.strptime(self.start_date_field.value.strip(), "%Y-%m-%d")
        except: return

        source_type = self.source_dropdown.value
        if source_type != "templates" or not self.current_items: return

        new_algorithm_items = []
        for item in self.current_items:
            copied_item = json.loads(json.dumps(item))
            day_offset = copied_item.get("dayNum", 1) - 1
            target_date = start_date + timedelta(days=day_offset)
            copied_item["date"] = target_date.strftime("%Y-%m-%d")
            copied_item["algorithmId"] = 99
            new_algorithm_items.append(copied_item)

        new_algorithm = {
            "id": 99,
            "name": f"Розклад з {start_date.strftime('%d.%m.%Y')} (Згенеровано)",
            "algorithmItems": new_algorithm_items
        }
        if "algorithms" not in self.json_data: self.json_data["algorithms"] = []
        self.json_data["algorithms"].insert(0, new_algorithm)
        self.close_gen_modal()
        self.source_dropdown.value = "algorithms"
        self.update_filter_dropdown("algorithms")

    def save_mobile_modal_data(self, e):
        item_data = self.current_items[self.selected_item_index]
        for key, field in self.input_fields.items(): item_data[key] = field.value
        self.close_modal()
        self.render_calendar_grid(self.filter_dropdown.value)

    def close_modal(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def close_gen_modal(self):
        if self.gen_dialog:
            self.gen_dialog.open = False
            self.page.update()

    def delete_mobile_item(self, index):
        self.current_items.pop(index)
        self.render_calendar_grid(self.filter_dropdown.value)

    def export_json_file(self, e):
        json_str = json.dumps(self.json_data, ensure_ascii=False, indent=2)
        self.page.set_clipboard(json_str)
        self.page.show_snack_bar(ft.SnackBar(ft.Text("Оновлений JSON скопійовано в буфер обміну телефона!")))

if __name__ == "__main__":
    app_instance = MilitaryMobileApp()
    ft.app(target=app_instance.build_main_ui, assets_dir="")
