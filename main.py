# Блок 2: Повний виправлений код main.py (Частина 1: Імпорт, Мапи та Конструктор класу)
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

SVG_MILITARY_ICON = """<svg xmlns="http://w3.org" viewBox="0 0 100 100" width="100" height="100">
  <circle cx="50" cy="50" r="46" fill="#1E231E" stroke="#00B050" stroke-width="2" />
  <circle cx="50" cy="50" r="40" fill="none" stroke="#00B050" stroke-width="3" />
  <circle cx="50" cy="50" r="43" fill="none" stroke="#00B050" stroke-width="1" stroke-dasharray="4 2" />
  <line x1="50" y1="5" x2="50" y2="25" stroke="#00B050" stroke-width="3" stroke-linecap="round" />
  <line x1="50" y1="75" x2="50" y2="95" stroke="#00B050" stroke-width="3" stroke-linecap="round" />
  <line x1="5" y1="50" x2="25" y2="50" stroke="#00B050" stroke-width="3" stroke-linecap="round" />
  <line x1="75" y1="50" x2="95" y2="50" stroke="#00B050" stroke-width="3" stroke-linecap="round" />
  <path d="M32 42 L50 57 L68 42 M32 52 L50 67 L68 52" fill="none" stroke="#FFD700" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

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
# Блок 3: Повний виправлений код main.py (Частина 2: Інтерфейс UI Панелі)
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
                ft.Row([
                    ft.Image(src_svg=SVG_MILITARY_ICON, width=38, height=32, fit=ft.ImageFit.CONTAIN),
                    ft.Text("Менеджер БЗВП", size=16, weight="bold", color="white")
                ], spacing=8),
                ft.Row([
                    ft.ElevatedButton("📁 JSON", icon=ft.icons.FOLDER_OPEN, on_click=lambda _: self.pick_file_dialog.pick_files()),
                    ft.ElevatedButton("📅 Тиждень", icon=ft.icons.DATE_RANGE, on_click=self.open_generate_week_modal),
                    ft.ElevatedButton("📤 Експорт", icon=ft.icons.SAVE, on_click=lambda _: self.save_file_dialog.save_file(file_name="schedule.json")),
                ]),
                ft.Row([
                    ft.IconButton(ft.icons.GROUP_ADD, tooltip="Додати підрозділ", icon_color="#4CAF50", on_click=self.open_add_group_modal),
                    ft.IconButton(ft.icons.DELETE_SWEEP, tooltip="Видалити цей підрозділ", icon_color="#E53935", on_click=self.delete_current_group),
                    ft.ElevatedButton("➕ Заняття", icon=ft.icons.ADD_CARD, bgcolor="#2E7D32", on_click=self.open_add_item_modal)
                ])
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
# Блок 4: Повний виправлений код main.py (Частина 3: Безпечна фільтрація та Ключі сортування)
    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if not e.files or not e.files.path: return
        try:
            file_path = e.files.path
            with open(file_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
            
            if isinstance(parsed_data, dict) and ("templates" in parsed_data or "algorithms" in parsed_data):
                self.json_data = parsed_data
                if "templates" not in self.json_data: self.json_data["templates"] = []
                if "algorithms" not in self.json_data: self.json_data["algorithms"] = []
                self.source_dropdown.value = "templates" if self.json_data["templates"] else "algorithms"
                self.update_filter_dropdown(self.source_dropdown.value)
            else:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Помилка структури розкладу у вашому JSON файлі!"), open=True))
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Помилка імпорту розкладу: {str(ex)}"), open=True))

    def on_source_changed(self, e):
        self.update_filter_dropdown(self.source_dropdown.value)

    def update_filter_dropdown(self, key):
        try:
            if self.json_data and key in self.json_data and isinstance(self.json_data[key], list) and len(self.json_data[key]) > 0:
                items = self.json_data[key]
                self.filter_dropdown.options = [ft.dropdown.Option(item["name"]) for item in items if "name" in item]
                self.filter_dropdown.value = items[0]["name"]
                self.render_calendar_grid(self.filter_dropdown.value)
            else:
                self.filter_dropdown.options = []
                self.filter_dropdown.value = None
                self.grid_scroll_row.controls.clear()
        except:
            self.filter_dropdown.options = []
            self.filter_dropdown.value = None
            self.grid_scroll_row.controls.clear()
        self.page.update()

    def on_filter_changed(self, e):
        self.render_calendar_grid(self.filter_dropdown.value)

    def get_day_sort_key(self, day_title_tuple):
        try:
            day_title = day_title_tuple[0]
            title_lower = stroke_str = str(day_title).lower()
            if len(title_lower) >= 10 and title_lower[0:4].isdigit() and "-" in title_lower:
                return (0, title_lower)
            if "день" in title_lower:
                num = int(''.join(filter(str.isdigit, title_lower)))
                return (1, num)
            for key, order in DAYS_ORDER.items():
                if key in title_lower: return (2, order)
            return (3, title_lower)
        except:
            return (4, "")
# Блок 5: Повний виправлений код main.py (Частина 4: Рендеринг сітки та обчислення годин)
    def render_calendar_grid(self, selected_name):
        try:
            self.grid_scroll_row.controls.clear()
            if not selected_name:
                self.page.update()
                return
                
            source_type = self.source_dropdown.value
            target_group = next((g for g in self.json_data.get(source_type, []) if g.get("name") == selected_name), None)
            if not target_group:
                self.page.update()
                return

            item_key = "templateItems" if source_type == "templates" else "algorithmItems"
            self.current_items = target_group.get(item_key, [])

            days_data = {}
            for idx, item in enumerate(self.current_items):
                if "date" in item and item["date"]:
                    try:
                        dt = datetime.strptime(item["date"], "%Y-%m-%d")
                        ukr_days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
                        day_key = f"{item['date']} ({ukr_days[dt.weekday()]})"
                    except: 
                        day_key = str(item["date"])
                else:
                    day_key = f"День {item.get('dayNum', 1)}"
                
                if day_key not in days_data: days_data[day_key] = []
                days_data[day_key].append((idx, item))

            ukr_days_lower = ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"]
            current_day_name = ukr_days_lower[datetime.now().weekday()]
            current_date_str = datetime.now().strftime("%Y-%m-%d")

            sorted_days = sorted(days_data.items(), key=self.get_day_sort_key)
# Блок 6: Повний виправлений код main.py (Частина 5: Побудова карток та Календарних колонок)
            today_col_index = None
            for col_idx, (day_title, items_list) in enumerate(sorted_days):
                day_column = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
                title_lower = str(day_title).lower()
                is_today = (current_day_name in title_lower) or (current_date_str in title_lower)

                if is_today:
                    today_col_index = col_idx

                sorted_items = sorted(items_list, key=lambda x: x[1].get("startTime", "00:00:00"))
                
                total_hours = 0
                for _, itm in sorted_items:
                    try: total_hours += int(itm.get("hours", 0))
                    except: pass
                
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
# Блок 7: Повний виправлений код main.py (Частина 6: Побудова занять та Скролінг на сьогодні)
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
                    content=day_column, width=220, 
                    bgcolor="#202220" if is_today else "#161716", 
                    border_radius=10, padding=8,
                    border=ft.border.all(2, "#00B050" if is_today else "#2D302D"),
                    height=550
                )
                self.grid_scroll_row.controls.append(day_container)
                
            self.page.update()
            
            if today_col_index is not None:
                try: self.grid_scroll_row.scroll_to(index=today_col_index, duration=500)
                except: pass
        except Exception as grid_ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Помилка гріда: {str(grid_ex)}"), open=True))
# Блок 8: Повний виправлений код main.py (Частина 7: Форма інспектування та зміни занять)
    def on_item_click(self, idx):
        self.selected_item_index = idx
        item = self.current_items[idx]
        
        day_input = ft.TextField(label="Номер дня / Дата (YYYY-MM-DD)", value=str(item.get("dayNum", item.get("date", ""))), width=250)
        start_input = ft.TextField(label="Час початку (HH:MM:SS)", value=item.get("startTime", "00:00:00"), width=250)
        end_input = ft.TextField(label="Час закінчення (HH:MM:SS)", value=item.get("endTime", "00:00:00"), width=250)
        subject_input = ft.TextField(label="Предмет", value=item.get("subject", ""), width=250)
        abbr_input = ft.TextField(label="Абревіатура", value=item.get("abbr", ""), width=250)
        ctype_input = ft.TextField(label="Тип (П) / (Л)", value=item.get("classType", ""), width=250)
        loc_input = ft.TextField(label="Локація", value=item.get("location", ""), width=250)
        hours_input = ft.TextField(label="Кількість годин", value=str(item.get("hours", 2)), width=250)

        def save_edited_item(_):
            val = day_input.value
            if "-" in val:
                item["date"] = val
                item.pop("dayNum", None)
            else:
                item["dayNum"] = int(val) if val.isdigit() else 1
                item.pop("date", None)
                
            item["startTime"] = start_input.value
            item["endTime"] = end_input.value
            item["subject"] = subject_input.value
            item["abbr"] = abbr_input.value
            item["classType"] = ctype_input.value
            item["location"] = loc_input.value
            item["hours"] = int(hours_input.value) if hours_input.value.isdigit() else 2
            
            self.page.dialog.open = False
            self.render_calendar_grid(self.filter_dropdown.value)

        def delete_item(_):
            self.current_items.pop(idx)
            self.page.dialog.open = False
            self.render_calendar_grid(self.filter_dropdown.value)

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Редагування заняття"),
            content=ft.Container(
                content=ft.Column([
                    day_input, start_input, end_input, subject_input,
                    abbr_input, ctype_input, loc_input, hours_input
                ], scroll=ft.ScrollMode.ADAPTIVE, tight=True),
                height=350, width=280
            ),
            actions=[
                ft.TextButton("Видалити", icon=ft.icons.DELETE, icon_color="red", on_click=delete_item),
                ft.TextButton("Скасувати", on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Зберегти", on_click=save_edited_item)
            ]
        )
        self.page.dialog.open = True
        self.page.update()
# Блок 9: Повний виправлений код main.py (Частина 8: Додавання нових карток у розклад)
    def open_add_item_modal(self, e):
        if not self.filter_dropdown.value: return

        day_input = ft.TextField(label="Номер дня або Дата (YYYY-MM-DD)", value="1", width=250)
        start_input = ft.TextField(label="Час початку (HH:MM:SS)", value="08:30:00", width=250)
        end_input = ft.TextField(label="Час закінчення (HH:MM:SS)", value="10:00:00", width=250)
        subject_input = ft.TextField(label="Предмет", placeholder="Введіть назву", width=250)
        abbr_input = ft.TextField(label="Абревіатура (напр. ВП 1/2)", placeholder="ВП", width=250)
        ctype_input = ft.TextField(label="Тип занять (П)/(Л)", value="(П)", width=250)
        loc_input = ft.TextField(label="Локація", value="Поле", width=250)
        hours_input = ft.TextField(label="Години", value="2", width=250)

        def confirm_add(_):
            new_item = {
                "id": len(self.current_items) + 1,
                "startTime": start_input.value,
                "endTime": end_input.value,
                "subject": subject_input.value if subject_input.value else "Нове заняття",
                "abbr": abbr_input.value if abbr_input.value else "СП",
                "classType": ctype_input.value,
                "location": loc_input.value,
                "hours": int(hours_input.value) if hours_input.value.isdigit() else 2,
                "chapter": "БЗВП", "topic": "", "notes": ""
            }
            val = day_input.value
            if "-" in val: new_item["date"] = val
            else: new_item["dayNum"] = int(val) if val.isdigit() else 1

            self.current_items.append(new_item)
            self.page.dialog.open = False
            self.render_calendar_grid(self.filter_dropdown.value)

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Додати нове заняття"),
            content=ft.Container(
                content=ft.Column([
                    day_input, start_input, end_input, subject_input,
                    abbr_input, ctype_input, loc_input, hours_input
                ], scroll=ft.ScrollMode.ADAPTIVE, tight=True),
                height=350, width=280
            ),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Додати", on_click=confirm_add)
            ]
        )
        self.page.dialog.open = True
        self.page.update()
# Блок 10: Повний виправлений код main.py (Частина 9: Управління підрозділами та модалки)
    def open_add_group_modal(self, e):
        name_input = ft.TextField(label="Назва підрозділу (Роти / Взводу)", placeholder="Наприклад: 2 Рота 1 Взвод", width=250)

        def confirm_group(_):
            if not name_input.value: return
            source_key = self.source_dropdown.value
            item_key = "templateItems" if source_key == "templates" else "algorithmItems"
            new_group = {"name": name_input.value, item_key: []}
            if source_key not in self.json_data: self.json_data[source_key] = []
            self.json_data[source_key].append(new_group)
            self.page.dialog.open = False
            self.filter_dropdown.options.append(ft.dropdown.Option(name_input.value))
            self.filter_dropdown.value = name_input.value
            self.render_calendar_grid(name_input.value)

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Створити підрозділ"),
            content=ft.Column([name_input], tight=True),
            actions=[
                ft.TextButton("Скасувати", on_click=lambda _: setattr(self.page.dialog, "open", False) or self.page.update()),
                ft.ElevatedButton("Створити", on_click=confirm_group)
            ]
        )
        self.page.dialog.open = True
        self.page.update()

    def delete_current_group(self, e):
        selected_name = self.filter_dropdown.value
        if not selected_name: return
        source_key = self.source_dropdown.value
        groups_list = self.json_data.get(source_key, [])
        target_group = next((g for g in groups_list if g["name"] == selected_name), None)
        if target_group:
            groups_list.remove(target_group)
            self.update_filter_dropdown(source_key)
# Блок 11: Повний виправлений код main.py (Частина 10: Генератор дат та запуск додатку)
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
            except Exception as ex:
                error_txt.value = f"Помилка: {str(ex)}"
                self.page.update()

        date_input = ft.TextField(label="Дата Понеділка (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"), width=250)
        error_txt = ft.Text(color="red")

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Генерація дат на тиждень"),
            content=ft.Column([
                ft.Text("Введіть дату початку тижня. Всі дні шаблону отримають календарні дати."),
                date_input, error_txt
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
        except: pass

def main(page: ft.Page):
    app = MilitaryMobileApp()
    app.build_main_ui(page)

if __name__ == "__main__":
    ft.app(target=main)
