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
                ft.ElevatedButton("📤 Експорт", icon=ft.icons.SAVE, on_click=lambda _: self.save_file_dialog.save_file(file_name="schedule.json"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([self.source_dropdown, self.filter_dropdown]),
            ft.Divider(),
            ft.Container(content=self.grid_scroll_row, expand=True)
        )

        self.pick_file_dialog = ft.FilePicker(on_result=self.on_file_picked)
        self.save_file_dialog = ft.FilePicker(on_result=self.on_file_saved)
        self.page.overlay.extend([self.pick_file_dialog, self.save_file_dialog])
        
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
            if isinstance(self.json_data[key], list) and len(self.json_data[key]) > 0:
                self.filter_dropdown.value = self.json_data[key][0]["name"]
            else:
                self.filter_dropdown.value = None
            self.render_calendar_grid(self.filter_dropdown.value)
        else:
            self.filter_dropdown.options = []
            self.filter_dropdown.value = None
            self.grid_scroll_row.controls.clear()
        self.page.update()

    def on_filter_changed(self, e):
        self.render_calendar_grid(self.filter_dropdown.value)

    def get_day_sort_key(self, item_tuple):
        day_title = item_tuple[0]
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

        sorted_days = sorted(days_data.items(), key=self.get_day_sort_key)

        today_index = None
        for i, (day_title, _) in enumerate(sorted_days):
            title_lower = str(day_title).lower()
            if (current_day_name in title_lower) or (current_date_str in title_lower):
                today_index = i
                break

        if today_index is not None and today_index > 0:
            sorted_days = sorted_days[today_index:] + sorted_days[:today_index]
        for col_idx, (day_title, items_list) in enumerate(sorted_days):
            day_column = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
            
            title_lower = str(day_title).lower()
            is_today = (current_day_name in title_lower) or (current_date_str in title_lower)

            sorted_items = sorted(items_list, key=lambda x: x[1].get("startTime", "00:00:00"))
            total_hours = sum(int(item.get("hours", 0)) for _, item in sorted_items)
            
            header_text = f"{day_title} [{total_hours} год]"
            if is_today: header_text += " (СЬОГОДНІ)"

            day_column.controls.append(
                ft.Container(
                    content=ft.Text(header_text, weight="bold", size=12, color="white"),
                    alignment=ft.alignment.center, padding=6, 
                    bgcolor="#00B050" if is_today else "#2D302D", 
                    border_radius=6
                )
            )
            for global_idx, item in sorted_items:
                subj = item.get("subject", "Невідомо")
                abbr = item.get("abbr", "")
                start_t = item.get("startTime", "")[:5] if item.get("startTime") else "00:00"
                end_t = item.get("endTime", "")[:5] if item.get("endTime") else "00:00"
                loc = item.get("location", "—")
                ctype = item.get("classType", "")

                clean_abbr = abbr.split()[0] if abbr else "СП"
                card_color = COLOR_MAP.get(clean_abbr, "#757575")

                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{start_t}-{end_t}", size=11, color="#B0B0B0"),
                            ft.Text(ctype, size=11, weight="bold", color="#FFD700" if "(П)" in ctype else "#808080")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(subj, size=13, weight="bold", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Row([
                            ft.Text(abbr, size=11, color="white", weight="bold"),
                            ft.Text(loc, size=11, color="#E0E0E0", italic=True)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=4),
                    padding=8,
                    bgcolor="#2C2F2C" if is_today else "#252625",
                    border_radius=6,
                    border=ft.border.all(1, card_color),
                    on_click=lambda _, idx=global_idx: self.on_item_click(idx)
                )
                day_column.controls.append(card)
            day_container = ft.Container(
                content=day_column, 
                width=220, 
                bgcolor="#202220" if is_today else "#161716", 
                border_radius=10, 
                padding=8,
                border=ft.border.all(2, "#00B050" if is_today else "#2D302D"),
                height=550
            )
            self.grid_scroll_row.controls.append(day_container)
            
        self.page.update()

    def on_item_click(self, idx):
        self.selected_item_index = idx
        item = self.current_items[idx]
        self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Обрано: {item.get('subject')} ({item.get('abbr')})"), open=True))
    def open_generate_week_modal(self, e):
        def confirm_generation(_):
            try:
                start_dt = datetime.strptime(date_input.value, "%Y-%m-%d")
                source_type = self.source_dropdown.value
                selected_name = self.filter_dropdown.value
                
                target_group = next((g for g in self.json_data.get(source_type, []) if g["name"] == selected_name), None)
                if target_group:
                    items_key = "templateItems" if source_type == "templates" else "algorithmItems"
                    for item in target_group.get(items_key, []):
                        day_offset = int(item.get("dayNum", 1)) - 1
                        target_date = start_dt + timedelta(days=day_offset)
                        item["date"] = target_date.strftime("%Y-%m-%d")
                    
                    self.page.dialog.open = False
                    self.render_calendar_grid(selected_name)
                    self.page.show_snack_bar(ft.SnackBar(ft.Text("Дати успішно згенеровано!"), open=True))
            except Exception as ex:
                error_txt.value = f"Помилка: {str(ex)}"
                self.page.update()

        date_input = ft.TextField(label="Дата Понеділка (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"), width=250)
        error_txt = ft.Text(color="red")
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Генерація дат на тиждень"),
            content=ft.Column([
                ft.Text("Введіть дату початку тижня. Всі дні шаблону автоматично отримають календарні дати."),
                date_input,
                error_txt
            ], tight=True, spacing=10),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Генерувати", on_click=confirm_generation)
            ]
        )
        self.page.dialog.open = True
        self.page.update()
    def on_file_saved(self, e: ft.FilePickerResultEvent):
        if not e.path: return
        try:
            with open(e.path, "w", encoding="utf-8") as f:
                json.dump(self.json_data, f, ensure_ascii=False, indent=4)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Файл успішно збережено!"), open=True))
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Помилка збереження: {str(ex)}"), open=True))

def main(page: ft.Page):
    app = MilitaryMobileApp()
    app.build_main_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
