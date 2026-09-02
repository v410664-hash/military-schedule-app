# Блок 1: Повний виправлений код додатка з усуненням помилки "чорного екрану"

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
        self.current_items =
        self.selected_item_index = None
        
        self.embedded_json = {
            "templates": [
                {
                    "name": " Рота  Взвод (Зразок)",
                    "templateItems": [
                        {"id": "dayNum": "startTime": "::", "endTime": "::", "chapter": "БЗВП", "subject": "Вогнева підготовка", "abbr": "ВП /", "classType": "(П)", "location": "Тир", "hours": "topic": "", "notes": ""},
                        {"id": "dayNum": "startTime": "::", "endTime": "::", "chapter": "БЗВП", "subject": "Тактична підготовка", "abbr": "ТП /", "classType": "(П)", "location": "Поле", "hours": "topic": "", "notes": ""}
                    ]
                }
            ],
            "algorithms":
        }
# Блок 2: Побудова UI та виправлений метод оновлення випадаючого списку (Dropdown)

    def build_main_ui(self, page: ft.Page):
        self.page = page
        self.page.title = "Менеджер БЗВП — Повний Екран Рот"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 10
        
        self.grid_scroll_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=15, expand=True)
        
        self.source_dropdown = ft.Dropdown(
            label="Категорія даних", width=140, on_change=self.on_source_changed, value="templates",
            options=[ftdropdownOption("templates", "Шаблони"), ftdropdownOption("algorithms", "Алгоритми")]
        )
        self.filter_dropdown = ft.Dropdown(label="Вибір Роти / Взводу", expand=True, on_change=self.on_filter_changed)

        self.page.add(
            ft.Row([
                ftRow([
                    ftImage(src_svg=SVG_MILITARY_ICON, width=height=fit=ftImageFitCONTAIN),
                    ftText("Менеджер БЗВП", size=weight="bold", color="white")
                ], spacing=8),
                ft.Row([
                    ftElevatedButton("📁 JSON", icon=fticonsFOLDER_OPEN, on_click=lambda _: selfpick_file_dialogpick_files()),
                    ftElevatedButton("📅 Тиждень", icon=fticonsDATE_RANGE, on_click=selfopen_generate_week_modal),
                    ftElevatedButton("📤 Експорт", icon=fticonsSAVE, on_click=lambda _: selfsave_file_dialogsave_file(file_name="schedulejson")),
                ]),
                ft.Row([
                    ftIconButton(fticonsGROUP_ADD, tooltip="Додати підрозділ", icon_color="#CAF", on_click=selfopen_add_group_modal),
                    ftIconButton(fticonsDELETE_SWEEP, tooltip="Видалити цей підрозділ", icon_color="#E", on_click=selfdelete_current_group),
                    ftElevatedButton("➕ Заняття", icon=fticonsADD_CARD, bgcolor="#ED", on_click=selfopen_add_item_modal)
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([selfsource_dropdown, selffilter_dropdown]),
            ft.Divider(),
            ft.Container(content=self.grid_scroll_row, expand=True)
        )

        self.pick_file_dialog = ft.FilePicker(on_result=self.on_file_picked)
        self.save_file_dialog = ft.FilePicker(on_result=self.on_file_saved)
        self.page.overlay.extend([selfpick_file_dialog, selfsave_file_dialog])
        
        self.json_data = self.embedded_json
        self.update_filter_dropdown("templates")

    def update_filter_dropdown(self, key):
        if self.json_data and key in self.json_data and self.json_data[key]:
            items = self.json_data[key]
            self.filter_dropdown.options = [ftdropdownOption(item["name"]) for item in items if "name" in item]
            
            # ВИПРАВЛЕНО: Замість неправильного items["name"] береться назва з першого елемента масиву items["name"]
            if len(items) > 0 and "name" in items:
                self.filter_dropdown.value = items["name"]
                self.render_calendar_grid(self.filter_dropdown.value)
            else:
                self.filter_dropdown.value = None
                self.grid_scroll_row.controls.clear()
        else:
            self.filter_dropdown.options =
            self.filter_dropdown.value = None
            self.grid_scroll_row.controls.clear()
        self.page.update()
# Блок 3: Обробники імпорту файлів та логіка сортування елементів розкладу

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if not e.files or not e.files.path: return
        try:
            file_path = e.files.path
            with open(file_path, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)
            
            if isinstance(parsed_data, dict) and ("templates" in parsed_data or "algorithms" in parsed_data):
                self.json_data = parsed_data
                if "templates" not in self.json_data: self.json_data["templates"] =
                if "algorithms" not in self.json_data: self.json_data["algorithms"] =
                
                # Автоматично вибираємо ту категорію, де є дані
                chosen_key = "templates" if self.json_data["templates"] else "algorithms"
                self.source_dropdown.value = chosen_key
                self.update_filter_dropdown(chosen_key)
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Розклад успішно завантажено!"), open=True))
            else:
                self.page.show_snack_bar(ft.SnackBar(ft.Text("Помилка структури розкладу у вашому JSON файлі!"), open=True))
        except Exception as ex:
            self.page.show_snack_bar(ft.SnackBar(ft.Text(f"Помилка імпорту розкладу: {str(ex)}"), open=True))

    def on_source_changed(self, e):
        self.update_filter_dropdown(self.source_dropdown.value)

    def on_filter_changed(self, e):
        self.render_calendar_grid(self.filter_dropdown.value)

    def get_day_sort_key(self, item_tuple):
        day_title = item_tuple
        title_lower = str(day_title).lower()
        
        if len(title_lower) >= 10 and title_lower[:].isdigit() and title_lower == '-' and title_lower == '-':
            return (0, title_lower)
            
        if "день" in title_lower:
            try:
                num = int(''.join(filter(str.isdigit, title_lower)))
                return (1, num)
            except:
                return (1, 999)
                
        for key, order in DAYS_ORDER.items():
            if key in title_lower:
                return (2, order)
                
        return (3, title_lower)
# Блок 4: Рендеринг колонок календаря з хронологічним сортуванням і прокруткою

    def render_calendar_grid(self, selected_name):
        self.grid_scroll_row.controls.clear()
        if not selected_name:
            self.page.update()
            return
            
        source_type = self.source_dropdown.value
        target_group = next((g for g in self.json_data.get(source_type,) if g["name"] == selected_name), None)
        if not target_group:
            self.page.update()
            return

        item_key = "templateItems" if source_type == "templates" else "algorithmItems"
        self.current_items = target_group.get(item_key,)

        days_data = {}
        for idx, item in enumerate(self.current_items):
            if "date" in item and item["date"]:
                try:
                    dt = datetime.strptime(item["date"], "%Y-%m-%d")
                    ukr_days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
                    day_key = f"{item['date']} ({ukr_days[dtweekday()]})"
                except: 
                    day_key = str(item["date"])
            else:
                day_key = f"День {item.get('dayNum', 1)}"
            
            if day_key not in days_data: 
                days_data[day_key] =
            days_data[day_key].append((idx, item))

        ukr_days_lower = ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"]
        current_day_name = ukr_days_lower[datetimenow()weekday()]
        current_date_str = datetime.now().strftime("%Y-%m-%d")

        sorted_days = sorted(days_data.items(), key=lambda x: self.get_day_sort_key(x))
# Блок 5: Побудова карток занять, відображення кольорів і розрахунок годин

        today_col_index = None
        for col_idx, (day_title, items_list) in enumerate(sorted_days):
            day_column = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
            title_lower = str(day_title).lower()
            is_today = (current_day_name in title_lower) or (current_date_str in title_lower)

            if is_today:
                today_col_index = col_idx

            sorted_items = sorted(items_list, key=lambda x: x.get("startTime", "00:00:00"))
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
                start_t = item.get("startTime", "")[:] if item.get("startTime") else "00:00"
                end_t = item.get("endTime", "")[:] if item.get("endTime") else "00:00"
                loc = item.get("location", "—")
                ctype = item.get("classType", "")

                clean_abbr = abbr.split() if abbr else "СП"
                card_color = COLOR_MAP.get(clean_abbr, "#757575")

                card = ft.Container(
                    content=ft.Column([
                        ftRow([
                            ftText(f"{start_t}-{end_t}", size=color="#BBB"),
                            ftText(ctype, size=weight="bold", color="#FFD" if "(П)" in ctype else "#")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(subj, size=13, weight="bold", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Row([
                            ftText(abbr, size=color="white", weight="bold"),
                            ftText(loc, size=color="#EEE", italic=True)
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
            try:
                self.grid_scroll_row.scroll_to(index=today_col_index, duration=500)
            except:
                pass
# Блок 6: Реалізація діалогового вікна редагування та видалення вибраного заняття

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
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Заняття оновлено!"), open=True))

        def delete_item(_):
            self.current_items.pop(idx)
            self.page.dialog.open = False
            self.render_calendar_grid(self.filter_dropdown.value)
            self.page.show_snack_bar(ft.SnackBar(ft.Text("Заняття видалено!"), open=True))

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
                ftTextButton("Видалити", icon=fticonsDELETE, icon_color="red", on_click=delete_item),
                ftTextButton("Скасувати", on_click=lambda _: setattr(selfpagedialog, "open", False) or selfpageupdate()),
                ftElevatedButton("Зберегти", on_click=save_edited_item)
            ]
        )
        self.page.dialog.open = True
        self.page.update()
