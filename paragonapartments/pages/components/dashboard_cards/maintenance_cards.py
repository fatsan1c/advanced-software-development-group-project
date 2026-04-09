"""Contributors: Oliver Mercer (24026901), Nickolas Greiner (24018357), Ollie Churchley (23020494)

Maintenance dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe


def load_front_desk_maintenance_card(self, row):
    maintenance_card = pe.FunctionCard(row, "Maintenance Requests", side="left")

    maint_button, maint_popup_func = pe.PopupCard(
        maintenance_card,
        button_text="Register Request",
        title="Register Maintenance Request",
        small=False,
        button_size="large",
    )

    def setup_maint_popup():
        from datetime import datetime

        content = maint_popup_func()

        scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=30, pady=20)

        entries = {}

        section_label = ctk.CTkLabel(
            scrollable,
            text="━━━━━━━━━━━━ Tenant & Property Details ━━━━━━━━━━━━",
            font=("Arial", 14, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        )
        section_label.pack(fill="x", pady=(0, 15))

        tenant_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        tenant_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(tenant_frame, text="Tenant ID *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
        entries["tenant_id"] = ctk.CTkEntry(tenant_frame, height=40, font=("Arial", 14), placeholder_text="Enter tenant ID number")
        entries["tenant_id"].pack(fill="x")

        apt_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        apt_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(apt_frame, text="Apartment ID *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
        entries["apartment_id"] = ctk.CTkEntry(apt_frame, height=40, font=("Arial", 14), placeholder_text="Enter apartment ID number")
        entries["apartment_id"].pack(fill="x")

        section_label2 = ctk.CTkLabel(
            scrollable,
            text="━━━━━━━━━━━━ Issue Details ━━━━━━━━━━━━",
            font=("Arial", 14, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        )
        section_label2.pack(fill="x", pady=(15, 15))

        issue_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        issue_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(issue_frame, text="Issue Description *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 5))
        entries["issue_description"] = ctk.CTkTextbox(issue_frame, height=120, font=("Arial", 14))
        entries["issue_description"].insert("1.0", "Describe the maintenance issue in detail...")
        entries["issue_description"].bind(
            "<FocusIn>",
            lambda e: entries["issue_description"].delete("1.0", "end")
            if entries["issue_description"].get("1.0", "end").strip() == "Describe the maintenance issue in detail..."
            else None,
        )
        entries["issue_description"].pack(fill="x")

        priority_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        priority_frame.pack(fill="x", pady=(12, 0))
        ctk.CTkLabel(priority_frame, text="Priority Level *", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0")).pack(anchor="w", pady=(0, 10))

        priority_var = ctk.StringVar(value="2")
        priority_options = ctk.CTkFrame(priority_frame, fg_color=("gray90", "gray17"), corner_radius=8)
        priority_options.pack(fill="x", pady=(0, 0))

        for level, label, color in [("3", "🔴 High Priority", "#C41E3A"), ("2", "🟡 Medium Priority", "#FFA500"), ("1", "🟢 Low Priority", "#2D862D")]:
            btn = ctk.CTkRadioButton(
                priority_options,
                text=label,
                variable=priority_var,
                value=level,
                font=("Arial", 14, "bold"),
                fg_color=("#1a3c5c", "#4196E0"),
                hover_color=("#0d2438", "#3380CC"),
            )
            btn.pack(side="left", padx=20, pady=15, expand=True)

        entries["priority_level"] = priority_var

        status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        status_frame.pack(fill="x", pady=(15, 0))

        error_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#C41E3A", "#FF6B6B"))
        success_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 13, "bold"), text_color=("#1a3c5c", "#4196E0"))

        def handle_submit():
            error_label.pack_forget()
            success_label.pack_forget()

            if not entries["tenant_id"].get().strip().isdigit():
                error_label.configure(text="❌ Error: Valid Tenant ID is required")
                error_label.pack(pady=10)
                return

            if not entries["apartment_id"].get().strip().isdigit():
                error_label.configure(text="❌ Error: Valid Apartment ID is required")
                error_label.pack(pady=10)
                return

            issue_text = entries["issue_description"].get("1.0", "end").strip()
            if not issue_text or issue_text == "Describe the maintenance issue in detail...":
                error_label.configure(text="❌ Error: Issue description is required")
                error_label.pack(pady=10)
                return

            values = {
                "tenant_id": int(entries["tenant_id"].get().strip()),
                "apartment_id": int(entries["apartment_id"].get().strip()),
                "issue_description": issue_text,
                "priority_level": int(entries["priority_level"].get()),
                "reported_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            result = self.register_maintenance_request(values)
            if result is True:
                success_label.configure(text="✓ Maintenance request registered successfully!")
                success_label.pack(pady=10)
                entries["tenant_id"].delete(0, "end")
                entries["apartment_id"].delete(0, "end")
                entries["issue_description"].delete("1.0", "end")
                entries["issue_description"].insert("1.0", "Describe the maintenance issue in detail...")
                entries["priority_level"].set("2")
            else:
                error_label.configure(text=f"❌ {str(result)}")
                error_label.pack(pady=10)

        submit_btn = ctk.CTkButton(
            scrollable,
            text="📝 Submit Maintenance Request",
            command=handle_submit,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color=("#1a3c5c", "#4196E0"),
            hover_color=("#0d2438", "#3380CC"),
        )
        submit_btn.pack(fill="x", pady=(20, 10))

    maint_button.configure(command=setup_maint_popup)

    view_button, view_popup_func = pe.PopupCard(
        maintenance_card,
        button_text="View Requests",
        title="All Maintenance Requests",
        small=False,
        button_size="large",
    )

    def setup_view_popup():
        content = view_popup_func()

        search_bar = ctk.CTkFrame(content, fg_color=("gray92", "gray18"), corner_radius=8)
        search_bar.pack(fill="x", padx=30, pady=(15, 4))

        search_row = ctk.CTkFrame(search_bar, fg_color="transparent")
        search_row.pack(fill="x", padx=12, pady=10)

        search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Search tenant, apartment or issue…",
            height=38,
            font=("Arial", 13),
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        status_filter = ctk.CTkOptionMenu(
            search_row,
            values=["All", "Pending", "Completed"],
            width=140,
            height=38,
            font=("Arial", 13),
            fg_color=("#1a3c5c", "#4196E0"),
            button_color=("#0d2438", "#3380CC"),
            button_hover_color=("#0a1d2e", "#2570B8"),
        )
        status_filter.set("All")
        status_filter.pack(side="left", padx=(0, 8))

        search_btn = ctk.CTkButton(
            search_row,
            text="Search",
            width=90,
            height=38,
            font=("Arial", 13, "bold"),
            fg_color=("#1a3c5c", "#4196E0"),
            hover_color=("#0d2438", "#3380CC"),
        )
        search_btn.pack(side="left", padx=(0, 5))

        clear_btn = ctk.CTkButton(
            search_row,
            text="Clear",
            width=70,
            height=38,
            font=("Arial", 13),
            fg_color=("gray65", "gray35"),
            hover_color=("gray55", "gray28"),
        )
        clear_btn.pack(side="left")

        scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=30, pady=(4, 20))

        _MAINT_PAGE_SIZE = 20
        _maint_page = {"n": 0}
        _maint_filter = {"term": "", "status": "All"}

        def _apply_maint_filter(rows):
            term = _maint_filter["term"].strip().lower()
            status = _maint_filter["status"]
            if term:
                rows = [
                    r
                    for r in rows
                    if term in str(r.get("tenant_name", "")).lower()
                    or term in str(r.get("apartment_address", "")).lower()
                    or term in str(r.get("issue_description", "")).lower()
                    or term in str(r.get("request_ID", ""))
                ]
            if status == "Pending":
                rows = [r for r in rows if not r.get("completed")]
            elif status == "Completed":
                rows = [r for r in rows if r.get("completed")]
            return rows

        def refresh_requests(page=0):
            _maint_page["n"] = page
            for widget in scrollable.winfo_children():
                widget.destroy()

            all_requests = self.get_maintenance_requests(location=self.location)
            all_requests = _apply_maint_filter(all_requests)
            total = len(all_requests)
            total_pages = max(1, (total + _MAINT_PAGE_SIZE - 1) // _MAINT_PAGE_SIZE)
            current_page = min(page, total_pages - 1)
            _maint_page["n"] = current_page
            start = current_page * _MAINT_PAGE_SIZE
            end = start + _MAINT_PAGE_SIZE
            requests = all_requests[start:end]

            if all_requests:
                summary_frame = ctk.CTkFrame(scrollable, fg_color=("gray95", "gray15"), corner_radius=10)
                summary_frame.pack(fill="x", pady=(0, 15))

                pending_count = sum(1 for r in all_requests if not r.get("completed"))
                completed_count = sum(1 for r in all_requests if r.get("completed"))

                showing = f"  (showing {start + 1}–{min(end, total)} of {total})"
                summary_text = f"📊 Total: {total}  |  ⏳ Pending: {pending_count}  |  ✓ Completed: {completed_count}{showing}"
                ctk.CTkLabel(
                    summary_frame,
                    text=summary_text,
                    font=("Arial", 13, "bold"),
                    text_color=("#1a3c5c", "#4196E0"),
                ).pack(pady=15)

                if total > _MAINT_PAGE_SIZE:
                    nav = ctk.CTkFrame(scrollable, fg_color="transparent")
                    nav.pack(fill="x", pady=(0, 10))
                    ctk.CTkLabel(nav, text=f"Page {current_page + 1} of {total_pages}", font=("Arial", 12)).pack(side="left", padx=(0, 10))
                    if current_page > 0:
                        ctk.CTkButton(
                            nav,
                            text="← Prev",
                            width=90,
                            height=32,
                            command=lambda p=current_page - 1: refresh_requests(p),
                            fg_color=("gray70", "gray30"),
                            hover_color=("gray60", "gray25"),
                        ).pack(side="left", padx=(0, 5))
                    if current_page < total_pages - 1:
                        ctk.CTkButton(
                            nav,
                            text="Next →",
                            width=90,
                            height=32,
                            command=lambda p=current_page + 1: refresh_requests(p),
                            fg_color=("#1a3c5c", "#4196E0"),
                            hover_color=("#0d2438", "#3380CC"),
                        ).pack(side="left")

                for req in requests:
                    req_frame = ctk.CTkFrame(scrollable, fg_color=("gray90", "gray17"), corner_radius=10)
                    req_frame.pack(fill="x", pady=(0, 12))

                    header_frame = ctk.CTkFrame(req_frame, fg_color="transparent")
                    header_frame.pack(fill="x", padx=20, pady=(15, 10))

                    is_completed = req.get("completed")
                    status_text = "✅ COMPLETED" if is_completed else "🚧 PENDING"
                    status_color = ("#2D862D", "#4CAF50") if is_completed else ("#FFA500", "#FFB347")

                    id_status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
                    id_status_frame.pack(fill="x")

                    ctk.CTkLabel(
                        id_status_frame,
                        text=f"Request #{req.get('request_ID', 'N/A')}",
                        font=("Arial", 16, "bold"),
                        text_color=("#1a3c5c", "#4196E0"),
                        anchor="w",
                    ).pack(side="left")

                    status_badge = ctk.CTkLabel(
                        id_status_frame,
                        text=status_text,
                        font=("Arial", 11, "bold"),
                        text_color="white",
                        fg_color=status_color,
                        corner_radius=5,
                    )
                    status_badge.pack(side="right", padx=5, ipadx=10, ipady=5)

                    priority = req.get("priority_level", 2)
                    if priority >= 5:
                        priority_text = "⛔ URGENT"
                        priority_color = ("#8B0000", "#B22222")
                    elif priority >= 4:
                        priority_text = "🟥 CRITICAL"
                        priority_color = ("#B22222", "#D32F2F")
                    elif priority == 3:
                        priority_text = "🔴 HIGH"
                        priority_color = ("#C41E3A", "#FF6B6B")
                    elif priority == 2:
                        priority_text = "🟡 MEDIUM"
                        priority_color = ("#FFA500", "#FFB347")
                    else:
                        priority_text = "🟢 LOW"
                        priority_color = ("#2D862D", "#4CAF50")

                    priority_badge = ctk.CTkLabel(
                        id_status_frame,
                        text=priority_text,
                        font=("Arial", 11, "bold"),
                        text_color="white",
                        fg_color=priority_color,
                        corner_radius=5,
                    )
                    priority_badge.pack(side="right", ipadx=10, ipady=5)

                    details_frame = ctk.CTkFrame(req_frame, fg_color="transparent")
                    details_frame.pack(fill="x", padx=20, pady=(5, 10))

                    left_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                    left_col.pack(side="left", fill="both", expand=True)
                    ctk.CTkLabel(left_col, text=f"👤 Tenant: {req.get('tenant_name', 'N/A')}", font=("Arial", 12), anchor="w").pack(fill="x", pady=2)
                    ctk.CTkLabel(left_col, text=f"🏠 Apartment: {req.get('apartment_address', 'N/A')}", font=("Arial", 12), anchor="w").pack(fill="x", pady=2)

                    right_col = ctk.CTkFrame(details_frame, fg_color="transparent")
                    right_col.pack(side="right", fill="both", expand=True)
                    ctk.CTkLabel(right_col, text=f"📅 Reported: {req.get('reported_date', 'N/A')}", font=("Arial", 12), anchor="w").pack(fill="x", pady=2)

                    issue_frame = ctk.CTkFrame(req_frame, fg_color=("gray85", "gray20"), corner_radius=5)
                    issue_frame.pack(fill="x", padx=20, pady=(0, 10))
                    ctk.CTkLabel(
                        issue_frame,
                        text=f"📋 Issue: {req.get('issue_description', 'N/A')}",
                        font=("Arial", 12),
                        justify="left",
                        anchor="w",
                        wraplength=600,
                    ).pack(padx=12, pady=10, fill="x")

                    button_frame = ctk.CTkFrame(req_frame, fg_color="transparent")
                    button_frame.pack(fill="x", padx=20, pady=(0, 15))

                    request_id = req.get("request_ID")
                    flag_text = "↩️ Mark as Pending" if is_completed else "✅ Mark as Completed"
                    flag_btn = ctk.CTkButton(
                        button_frame,
                        text=flag_text,
                        command=lambda rid=request_id, completed=is_completed: handle_flag_request(rid, completed),
                        height=38,
                        font=("Arial", 13, "bold"),
                        fg_color=("#4196E0", "#3380CC") if not is_completed else ("#FFA500", "#FF8C00"),
                        hover_color=("#3380CC", "#2570B8") if not is_completed else ("#FF8C00", "#E67E00"),
                        width=200,
                    )
                    flag_btn.pack(side="left", padx=(0, 10))

                    delete_btn = ctk.CTkButton(
                        button_frame,
                        text="🗑️ Delete",
                        command=lambda rid=request_id: handle_delete_request(rid),
                        height=38,
                        font=("Arial", 13, "bold"),
                        fg_color=("#C41E3A", "#FF6B6B"),
                        hover_color=("#A01828", "#E65A5A"),
                        width=130,
                    )
                    delete_btn.pack(side="left")
            else:
                no_msg = "📭 No requests match your search" if _maint_filter["term"] or _maint_filter["status"] != "All" else "📭 No maintenance requests found"
                ctk.CTkLabel(scrollable, text=no_msg, font=("Arial", 15), text_color=("gray50", "gray60")).pack(pady=40)

        def _do_maint_search():
            _maint_filter["term"] = search_entry.get()
            _maint_filter["status"] = status_filter.get()
            refresh_requests(0)

        def _do_maint_clear():
            search_entry.delete(0, "end")
            status_filter.set("All")
            _maint_filter["term"] = ""
            _maint_filter["status"] = "All"
            refresh_requests(0)

        search_btn.configure(command=_do_maint_search)
        clear_btn.configure(command=_do_maint_clear)
        search_entry.bind("<Return>", lambda _e: _do_maint_search())

        def handle_flag_request(request_id, current_status):
            try:
                new_status = 0 if current_status else 1
                self.update_maintenance_request(request_id, completed=new_status)
                refresh_requests(_maint_page["n"])
            except Exception as e:
                print(f"Error flagging request: {e}")

        def handle_delete_request(request_id):
            try:
                self.delete_maintenance_request(request_id)
                refresh_requests(_maint_page["n"])
            except Exception as e:
                print(f"Error deleting request: {e}")

        refresh_requests(0)

    view_button.configure(command=setup_view_popup)


def load_maintenance_summary_card(self, row):
    summary_card = pe.FunctionCard(row, "Maintenance Summary", side="left")

    info_row = ctk.CTkFrame(summary_card, fg_color="transparent")
    info_row.pack(fill="x", pady=(0, 6))

    priority_badge = pe.InfoBadge(info_row, "High Priority: 0")

    location_dropdown = pe.LocationDropdownWithLabel(info_row)
    location_dropdown.set(self.location if self.location else "All Locations")

    stats = pe.StatsGrid(summary_card)

    total_value = pe.StatCard(stats, "Total Requests", "0")
    pending_value = pe.StatCard(stats, "Pending", "0")
    completed_value = pe.StatCard(stats, "Completed", "0")
    cost_value = pe.StatCard(stats, "Avg Cost", "£0.00")

    def update_summary(choice=None):
        try:
            location = pe.normalize_location_value(location_dropdown.get())
            stats_data = self.get_maintenance_stats(location)

            total = stats_data.get("total_requests", 0) or 0
            pending = stats_data.get("pending_requests", 0) or 0
            completed = stats_data.get("completed_requests", 0) or 0
            high_priority = stats_data.get("high_priority_pending", 0) or 0
            avg_cost = stats_data.get("avg_cost", 0) or 0

            total_value.configure(text=str(total))
            pending_value.configure(text=str(pending))
            completed_value.configure(text=str(completed))
            cost_value.configure(text=f"£{avg_cost:.2f}")
            priority_badge.configure(text=f"High Priority: {high_priority}")
        except Exception as e:
            print(f"Error loading maintenance stats: {e}")

    update_summary()
    refresh_timer, schedule_refresh = pe.create_debounced_refresh(summary_card, update_summary)
    location_dropdown.configure(command=schedule_refresh)


def load_maintenance_pending_requests_card(self, row):
    pending_card = pe.FunctionCard(row, "View Requests", side="left")

    button, open_popup = pe.PopupCard(
        pending_card,
        title="Pending Maintenance Requests",
        button_text="View Pending Requests",
        small=False,
        button_size="medium",
    )
    pe.style_accent_secondary_button(button)
    button.pack(pady=(0, 14))

    def setup_popup():
        content = open_popup()

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

        try:
            cities = ["All Locations"] + self.get_all_cities()
        except Exception as e:
            print(f"Error loading cities: {e}")
            cities = ["All Locations"]

        location_dropdown = ctk.CTkComboBox(header, values=cities, width=180, font=("Arial", 13))
        location_dropdown.set(self.location if self.location else "All Locations")
        location_dropdown.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(header, text="Priority:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

        priority_dropdown = ctk.CTkComboBox(
            header,
            values=["All", "1 - Low", "2", "3 - Medium", "4", "5 - Urgent"],
            width=140,
            font=("Arial", 13),
        )
        priority_dropdown.set("All")
        priority_dropdown.pack(side="left")

        columns = [
            {"name": "ID", "key": "request_ID", "width": 40, "editable": False},
            {"name": "Tenant", "key": "tenant_name", "width": 120, "editable": False},
            {"name": "Apartment", "key": "apartment_address", "width": 180, "editable": False},
            {"name": "City", "key": "city", "width": 70, "editable": False},
            {"name": "Issue", "key": "issue_description", "width": 250},
            {
                "name": "Priority",
                "key": "priority_level",
                "width": 65,
                "format": "dropdown",
                "options": [1, 2, 3, 4, 5],
            },
            {"name": "Reported", "key": "reported_date", "width": 80, "editable": False, "format": "date"},
            {"name": "Scheduled", "key": "scheduled_date", "width": 80, "format": "date"},
        ]

        def get_data():
            try:
                location = pe.normalize_location_value(location_dropdown.get())
                priority_val = priority_dropdown.get()
                priority = None
                if priority_val != "All":
                    priority = int(priority_val.split(" ")[0])
                return self.get_maintenance_requests(location=location, completed=0, priority=priority)
            except Exception as e:
                print(f"Error loading pending requests: {e}")
                return []

        table = pe.DataTable(
            content,
            columns,
            editable=False,
            deletable=False,
            refresh_data=get_data,
            show_refresh_button=False,
            render_batch_size=20,
            page_size=10,
        )
        _, refresh_table = table.table_container, table.refresh_table

        ctk.CTkButton(
            header,
            text="⟳ Refresh",
            command=refresh_table,
            height=32,
            width=120,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray25"),
        ).pack(side="left", padx=(12, 0))

        refresh_timer = {"id": None}

        def schedule_refresh(_choice=None):
            if refresh_timer["id"] is not None:
                try:
                    content.after_cancel(refresh_timer["id"])
                except Exception:
                    pass
            if hasattr(refresh_table, "reset_page"):
                refresh_table.reset_page()
            refresh_timer["id"] = content.after(150, refresh_table)

        location_dropdown.configure(command=schedule_refresh)
        priority_dropdown.configure(command=schedule_refresh)

    button.configure(command=setup_popup)

    _load_scheduled_maintenance_button(self, pending_card)
    _load_all_requests_button(self, pending_card)


def load_maintenance_complete_request_card(self, row):
    complete_card = pe.FunctionCard(row, "Complete Request", side="left")

    def fetch_requests():
        return self.get_maintenance_requests(
            location=self.location if self.location else "all",
            completed=0,
        )

    def format_request(req):
        issue_short = req["issue_description"][:40] + "..." if len(req["issue_description"]) > 40 else req["issue_description"]
        display = f"ID {req['request_ID']}: {issue_short} - {req['tenant_name']} (P{req['priority_level']})"
        return (display, req["request_ID"])

    def handle_submit(values):
        request_id = values.get("Select Request")

        if not request_id:
            return "Please select a request"

        submit_values = {
            "Request ID": request_id,
            "Final Cost": values.get("Final Cost", ""),
        }

        return self.complete_maintenance_request(submit_values)

    fields = [
        {
            "name": "Select Request",
            "type": "dropdown",
            "subtype": "dynamic",
            "required": True,
            "options": {
                "data_fetcher": fetch_requests,
                "display_formatter": format_request,
                "empty_message": "No pending requests",
            },
        },
        {
            "name": "Final Cost",
            "type": "text",
            "subtype": "currency",
            "required": False,
            "placeholder": "£0.00",
        },
    ]

    pe.Form(
        complete_card,
        fields,
        name="",
        submit_text="Mark Complete",
        on_submit=handle_submit,
        field_per_row=1,
    )


def load_maintenance_schedule_request_card(self, row):
    schedule_card = pe.FunctionCard(row, "Schedule Request", side="left")

    def fetch_requests():
        return self.get_maintenance_requests(
            location=self.location if self.location else "all",
            completed=0,
        )

    def format_request(req):
        issue_short = req["issue_description"][:30] + "..." if len(req["issue_description"]) > 30 else req["issue_description"]
        scheduled_status = f"[Scheduled: {req['scheduled_date']}]" if req["scheduled_date"] else "[Not Scheduled]"
        display = f"ID {req['request_ID']}: {issue_short} - {req['tenant_name']} (P{req['priority_level']}) {scheduled_status}"
        return (display, req["request_ID"])

    def handle_submit(values):
        request_id = values.get("Select Request")

        if not request_id:
            return "Please select a request"

        submit_values = {
            "Request ID": request_id,
            "Scheduled Date": values.get("Scheduled Date", ""),
        }

        return self.schedule_maintenance(submit_values)

    fields = [
        {
            "name": "Select Request",
            "type": "dropdown",
            "subtype": "dynamic",
            "required": True,
            "options": {
                "data_fetcher": fetch_requests,
                "display_formatter": format_request,
                "empty_message": "No pending requests",
            },
        },
        {
            "name": "Scheduled Date",
            "type": "text",
            "subtype": "date",
            "required": True,
            "placeholder": "YYYY-MM-DD",
        },
    ]

    pe.Form(
        schedule_card,
        fields,
        name="",
        submit_text="Schedule Request",
        on_submit=handle_submit,
        field_per_row=1,
    )


def load_maintenance_create_request_card(self, row):
    create_card = pe.FunctionCard(row, "Create Request", side="left")

    def fetch_apartments():
        return self.get_apartments_with_tenants(self.location)

    def format_apartment(apt):
        display = f"{apt['apartment_address']} - {apt['tenant_name']} ({apt['city']})"
        value = {
            "apartment_id": apt["apartment_ID"],
            "tenant_id": apt["tenant_ID"],
        }
        return (display, value)

    def handle_submit(values):
        apt_info = values.get("Select Apartment")

        if not apt_info or not isinstance(apt_info, dict):
            return "Please select an apartment"

        priority_str = values.get("Priority Level", "3 - Medium")
        priority = int(priority_str.split(" ")[0])

        submit_values = {
            "Apartment ID": apt_info["apartment_id"],
            "Tenant ID": apt_info["tenant_id"],
            "Issue Description": values.get("Issue Description", ""),
            "Priority Level": priority,
            "Scheduled Date": values.get("Scheduled Date", ""),
            "Cost Estimate": values.get("Cost Estimate", ""),
        }

        return self.create_maintenance_request(submit_values)

    fields = [
        {
            "name": "Select Apartment",
            "type": "dropdown",
            "subtype": "dynamic",
            "required": True,
            "options": {
                "data_fetcher": fetch_apartments,
                "display_formatter": format_apartment,
                "empty_message": "No apartments with active leases",
            },
        },
        {
            "name": "Issue Description",
            "type": "text",
            "required": True,
            "placeholder": "Describe the maintenance issue",
        },
        {
            "name": "Priority Level",
            "type": "dropdown",
            "options": ["1 - Low", "2", "3 - Medium", "4", "5 - Urgent"],
            "default": "3 - Medium",
            "required": True,
        },
        {
            "name": "Cost Estimate",
            "type": "text",
            "subtype": "currency",
            "required": False,
            "placeholder": "£0.00",
        },
        {
            "name": "Scheduled Date",
            "type": "text",
            "subtype": "date",
            "required": False,
            "placeholder": "YYYY-MM-DD",
        },
    ]

    pe.Form(
        create_card,
        fields,
        name="",
        submit_text="Create Request",
        on_submit=handle_submit,
        field_per_row=2,
    )


def _load_scheduled_maintenance_button(self, parent):
    button, open_popup = pe.PopupCard(
        parent,
        title="Upcoming Scheduled Maintenance",
        button_text="View Upcoming Schedule",
        button_size="medium",
    )
    pe.style_accent_secondary_button(button)
    button.pack(pady=(0, 10))

    def setup_popup():
        content = open_popup()

        columns = [
            {"name": "ID", "key": "request_ID", "width": 40, "editable": False},
            {"name": "Scheduled", "key": "scheduled_date", "width": 85, "editable": False, "format": "date"},
            {"name": "Priority", "key": "priority_level", "width": 65, "editable": False},
            {"name": "Tenant", "key": "tenant_name", "width": 120, "editable": False},
            {"name": "Apartment", "key": "apartment_address", "width": 180, "editable": False},
            {"name": "City", "key": "city", "width": 70, "editable": False},
            {"name": "Issue", "key": "issue_description", "width": 250, "editable": False},
            {"name": "Est. Cost", "key": "cost", "width": 100, "format": "currency", "editable": False},
        ]

        def get_data(location):
            try:
                return self.get_scheduled_maintenance(location)
            except Exception as e:
                print(f"Error loading scheduled maintenance: {e}")
                return []

        popup = pe.ViewableTablePopup(
            content,
            columns,
            get_data_func=get_data,
            include_location_filter=True,
            location_mapper=pe.normalize_location_value,
        )

        if popup.location_dropdown is not None:
            popup.location_dropdown.set(self.location if self.location else "All Locations")
            popup.table.refresh_table()

    button.configure(command=setup_popup)


def _load_all_requests_button(self, parent):
    button, open_popup = pe.PopupCard(
        parent,
        title="Maintenance Requests",
        button_text="View / Edit All Requests",
        small=False,
        button_size="medium",
    )
    pe.style_secondary_button(button)

    def setup_popup():
        content = open_popup()

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

        try:
            cities = ["All Locations"] + self.get_all_cities()
        except Exception as e:
            print(f"Error loading cities: {e}")
            cities = ["All Locations"]

        location_dropdown = ctk.CTkComboBox(header, values=cities, width=180, font=("Arial", 13))
        location_dropdown.set(self.location if self.location else "All Locations")
        location_dropdown.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(header, text="Status:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))

        status_dropdown = ctk.CTkComboBox(
            header,
            values=["All", "Pending", "Completed"],
            width=140,
            font=("Arial", 13),
        )
        status_dropdown.set("All")
        status_dropdown.pack(side="left")

        columns = [
            {"name": "ID", "key": "request_ID", "width": 35, "editable": False},
            {"name": "Tenant", "key": "tenant_name", "width": 70, "editable": False},
            {"name": "Apartment", "key": "apartment_address", "width": 80, "editable": False},
            {"name": "City", "key": "city", "width": 50, "editable": False},
            {"name": "Issue", "key": "issue_description", "width": 250},
            {"name": "P.", "key": "priority_level", "width": 25, "format": "dropdown", "options": ["1", "2", "3", "4", "5"]},
            {"name": "Reported", "key": "reported_date", "width": 70, "editable": False, "format": "date"},
            {"name": "Scheduled", "key": "scheduled_date", "width": 70, "format": "date"},
            {"name": "Done", "key": "completed", "width": 45, "format": "boolean"},
            {"name": "Cost", "key": "cost", "width": 55, "format": "currency"},
        ]

        def get_data():
            try:
                location = pe.normalize_location_value(location_dropdown.get())
                status_val = status_dropdown.get()
                completed = None
                if status_val == "Pending":
                    completed = 0
                elif status_val == "Completed":
                    completed = 1
                return self.get_maintenance_requests(location=location, completed=completed, compact=True)
            except Exception as e:
                print(f"Error loading maintenance requests: {e}")
                return []

        table = pe.DataTable(
            content,
            columns,
            editable=True,
            deletable=True,
            refresh_data=get_data,
            on_delete=self.delete_maintenance_request_row,
            on_update=self.update_maintenance_request_row,
            show_refresh_button=False,
            render_batch_size=20,
            page_size=10,
        )
        _, refresh_table = table.table_container, table.refresh_table

        pe.create_refresh_button(header, refresh_table, side="left", padx=(12, 0))

        refresh_timer = {"id": None}

        def schedule_refresh(_choice=None):
            if refresh_timer["id"] is not None:
                try:
                    content.after_cancel(refresh_timer["id"])
                except Exception:
                    pass
            if hasattr(refresh_table, "reset_page"):
                refresh_table.reset_page()
            refresh_timer["id"] = content.after(150, refresh_table)

        location_dropdown.configure(command=schedule_refresh)
        status_dropdown.configure(command=schedule_refresh)

    button.configure(command=setup_popup)
