"""Complaint dashboard card builders."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe


def load_front_desk_complaints_card(self, row):
    complaints_card = pe.FunctionCard(row, "Complaints", side="left")

    complaint_button, complaint_popup_func = pe.PopupCard(
        complaints_card,
        button_text="Register Complaint",
        title="Register Tenant Complaint",
        small=False,
        button_size="medium",
    )

    def setup_complaint_popup():
        from datetime import datetime

        content = complaint_popup_func()

        scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=30, pady=20)

        entries = {}

        section_label = ctk.CTkLabel(
            scrollable,
            text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📋 TENANT INFORMATION\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            font=("Arial", 14, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
            justify="center",
        )
        section_label.pack(fill="x", pady=(0, 15))

        tenant_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        tenant_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            tenant_frame,
            text="👤 Tenant ID *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))
        entries["tenant_id"] = ctk.CTkEntry(
            tenant_frame,
            height=40,
            font=("Arial", 14),
            placeholder_text="Enter tenant ID number",
        )
        entries["tenant_id"].pack(fill="x")

        section_label2 = ctk.CTkLabel(
            scrollable,
            text="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💬 COMPLAINT DETAILS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            font=("Arial", 14, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
            justify="center",
        )
        section_label2.pack(fill="x", pady=(20, 15))

        desc_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        desc_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            desc_frame,
            text="📝 Complaint Description *",
            font=("Arial", 13, "bold"),
            text_color=("#1a3c5c", "#4196E0"),
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(
            desc_frame,
            text="Please provide detailed information about the complaint",
            font=("Arial", 10),
            text_color=("gray50", "gray60"),
        ).pack(anchor="w", pady=(0, 8))

        entries["description"] = ctk.CTkTextbox(
            desc_frame,
            height=180,
            font=("Arial", 14),
            wrap="word",
        )
        entries["description"].pack(fill="x")

        status_frame = ctk.CTkFrame(scrollable, fg_color="transparent")
        status_frame.pack(fill="x", pady=(15, 0))

        error_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Arial", 13, "bold"),
            text_color=("#C41E3A", "#FF6B6B"),
        )
        success_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Arial", 13, "bold"),
            text_color=("#2D862D", "#4CAF50"),
        )

        def handle_submit():
            error_label.pack_forget()
            success_label.pack_forget()

            if not entries["tenant_id"].get().strip().isdigit():
                error_label.configure(text="❌ Error: Valid Tenant ID is required")
                error_label.pack(pady=10)
                return

            if not entries["description"].get("1.0", "end").strip():
                error_label.configure(text="❌ Error: Complaint description is required")
                error_label.pack(pady=10)
                return

            values = {
                "tenant_id": int(entries["tenant_id"].get().strip()),
                "description": entries["description"].get("1.0", "end").strip(),
                "date_submitted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            result = self.register_complaint(values)
            if result is True:
                success_label.configure(text="✅ Complaint registered successfully!")
                success_label.pack(pady=10)
                entries["tenant_id"].delete(0, "end")
                entries["description"].delete("1.0", "end")
            else:
                error_label.configure(text=f"❌ {str(result)}")
                error_label.pack(pady=10)

        submit_btn = ctk.CTkButton(
            scrollable,
            text="📝 Register Complaint",
            command=handle_submit,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color=("#1a3c5c", "#4196E0"),
            hover_color=("#0d2438", "#3380CC"),
        )
        submit_btn.pack(fill="x", pady=(20, 10))

    complaint_button.configure(command=setup_complaint_popup)

    view_complaint_button, view_complaint_popup_func = pe.PopupCard(
        complaints_card,
        button_text="View Complaints",
        title="All Tenant Complaints",
        small=False,
        button_size="medium",
    )

    def setup_view_complaint_popup():
        content = view_complaint_popup_func()

        search_bar_c = ctk.CTkFrame(content, fg_color=("gray92", "gray18"), corner_radius=8)
        search_bar_c.pack(fill="x", padx=30, pady=(15, 4))

        search_row_c = ctk.CTkFrame(search_bar_c, fg_color="transparent")
        search_row_c.pack(fill="x", padx=12, pady=10)

        search_entry_c = ctk.CTkEntry(
            search_row_c,
            placeholder_text="Search tenant name or complaint text…",
            height=38,
            font=("Arial", 13),
        )
        search_entry_c.pack(side="left", fill="x", expand=True, padx=(0, 8))

        status_filter_c = ctk.CTkOptionMenu(
            search_row_c,
            values=["All", "Pending", "Resolved"],
            width=140,
            height=38,
            font=("Arial", 13),
            fg_color=("#1a3c5c", "#4196E0"),
            button_color=("#0d2438", "#3380CC"),
            button_hover_color=("#0a1d2e", "#2570B8"),
        )
        status_filter_c.set("All")
        status_filter_c.pack(side="left", padx=(0, 8))

        search_btn_c = ctk.CTkButton(
            search_row_c,
            text="Search",
            width=90,
            height=38,
            font=("Arial", 13, "bold"),
            fg_color=("#1a3c5c", "#4196E0"),
            hover_color=("#0d2438", "#3380CC"),
        )
        search_btn_c.pack(side="left", padx=(0, 5))

        clear_btn_c = ctk.CTkButton(
            search_row_c,
            text="Clear",
            width=70,
            height=38,
            font=("Arial", 13),
            fg_color=("gray65", "gray35"),
            hover_color=("gray55", "gray28"),
        )
        clear_btn_c.pack(side="left")

        scrollable = ctk.CTkScrollableFrame(content, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=30, pady=(4, 20))

        _COMP_PAGE_SIZE = 20
        _comp_page = {"n": 0}
        _comp_filter = {"term": "", "status": "All"}

        def _apply_comp_filter(rows):
            term = _comp_filter["term"].strip().lower()
            status = _comp_filter["status"]
            if term:
                rows = [
                    r
                    for r in rows
                    if term in str(r.get("tenant_name", "")).lower()
                    or term in str(r.get("description", "")).lower()
                    or term in str(r.get("complaint_ID", ""))
                ]
            if status == "Pending":
                rows = [r for r in rows if not r.get("resolved")]
            elif status == "Resolved":
                rows = [r for r in rows if r.get("resolved")]
            return rows

        def refresh_complaints(page=0):
            _comp_page["n"] = page
            for widget in scrollable.winfo_children():
                widget.destroy()

            all_complaints = self.get_all_complaints()
            all_complaints = _apply_comp_filter(all_complaints)
            total = len(all_complaints)
            total_pages = max(1, (total + _COMP_PAGE_SIZE - 1) // _COMP_PAGE_SIZE)
            current_page = min(page, total_pages - 1)
            _comp_page["n"] = current_page
            start = current_page * _COMP_PAGE_SIZE
            end = start + _COMP_PAGE_SIZE
            complaints = all_complaints[start:end]

            if all_complaints:
                summary_frame = ctk.CTkFrame(scrollable, fg_color=("gray95", "gray15"), corner_radius=10)
                summary_frame.pack(fill="x", pady=(0, 15))

                pending_count = sum(1 for c in all_complaints if not c.get("resolved"))
                resolved_count = sum(1 for c in all_complaints if c.get("resolved"))

                showing = f"  (showing {start + 1}–{min(end, total)} of {total})"
                summary_text = f"💬 Total: {total}  |  🚧 Pending: {pending_count}  |  ✅ Resolved: {resolved_count}{showing}"
                ctk.CTkLabel(
                    summary_frame,
                    text=summary_text,
                    font=("Arial", 13, "bold"),
                    text_color=("#1a3c5c", "#4196E0"),
                ).pack(pady=15)

                if total > _COMP_PAGE_SIZE:
                    nav = ctk.CTkFrame(scrollable, fg_color="transparent")
                    nav.pack(fill="x", pady=(0, 10))
                    ctk.CTkLabel(nav, text=f"Page {current_page + 1} of {total_pages}", font=("Arial", 12)).pack(side="left", padx=(0, 10))
                    if current_page > 0:
                        ctk.CTkButton(
                            nav,
                            text="← Prev",
                            width=90,
                            height=32,
                            command=lambda p=current_page - 1: refresh_complaints(p),
                            fg_color=("gray70", "gray30"),
                            hover_color=("gray60", "gray25"),
                        ).pack(side="left", padx=(0, 5))
                    if current_page < total_pages - 1:
                        ctk.CTkButton(
                            nav,
                            text="Next →",
                            width=90,
                            height=32,
                            command=lambda p=current_page + 1: refresh_complaints(p),
                            fg_color=("#1a3c5c", "#4196E0"),
                            hover_color=("#0d2438", "#3380CC"),
                        ).pack(side="left")

                for comp in complaints:
                    comp_frame = ctk.CTkFrame(scrollable, fg_color=("gray90", "gray17"), corner_radius=10)
                    comp_frame.pack(fill="x", pady=(0, 12))

                    header_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
                    header_frame.pack(fill="x", padx=20, pady=(15, 10))

                    is_resolved = comp.get("resolved")
                    status_text = "✅ RESOLVED" if is_resolved else "🚧 PENDING"
                    status_color = ("#2D862D", "#4CAF50") if is_resolved else ("#FFA500", "#FFB347")

                    id_status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
                    id_status_frame.pack(fill="x")

                    ctk.CTkLabel(
                        id_status_frame,
                        text=f"Complaint #{comp.get('complaint_ID', 'N/A')}",
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
                    status_badge.pack(side="right", ipadx=10, ipady=5)

                    details_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
                    details_frame.pack(fill="x", padx=20, pady=(5, 10))
                    ctk.CTkLabel(details_frame, text=f"👤 Tenant: {comp.get('tenant_name', 'N/A')}", font=("Arial", 12), anchor="w").pack(fill="x", pady=2)
                    ctk.CTkLabel(details_frame, text=f"📅 Submitted: {comp.get('date_submitted', 'N/A')}", font=("Arial", 12), anchor="w").pack(fill="x", pady=2)

                    desc_section = ctk.CTkFrame(comp_frame, fg_color="transparent")
                    desc_section.pack(fill="x", padx=20, pady=(5, 10))
                    ctk.CTkLabel(
                        desc_section,
                        text="📝 Description:",
                        font=("Arial", 12, "bold"),
                        text_color=("#1a3c5c", "#4196E0"),
                        anchor="w",
                    ).pack(fill="x", pady=(0, 5))

                    desc_box = ctk.CTkTextbox(
                        desc_section,
                        height=80,
                        font=("Arial", 12),
                        fg_color=("gray85", "gray25"),
                        wrap="word",
                    )
                    desc_box.pack(fill="x")
                    desc_box.insert("1.0", comp.get("description", "N/A"))
                    desc_box.configure(state="disabled")

                    button_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
                    button_frame.pack(fill="x", padx=20, pady=(5, 15))

                    complaint_id = comp.get("complaint_ID")
                    flag_text = "↩️ Mark as Pending" if is_resolved else "✅ Mark as Resolved"
                    flag_btn = ctk.CTkButton(
                        button_frame,
                        text=flag_text,
                        command=lambda cid=complaint_id, resolved=is_resolved: handle_flag_complaint(cid, resolved),
                        height=38,
                        font=("Arial", 13, "bold"),
                        fg_color=("#4196E0", "#3380CC") if not is_resolved else ("#FFA500", "#FF8C00"),
                        hover_color=("#3380CC", "#2570B8") if not is_resolved else ("#FF8C00", "#E67E00"),
                        width=200,
                    )
                    flag_btn.pack(side="left", padx=(0, 10))

                    delete_btn = ctk.CTkButton(
                        button_frame,
                        text="🗑️ Delete",
                        command=lambda cid=complaint_id: handle_delete_complaint(cid),
                        height=38,
                        font=("Arial", 13, "bold"),
                        fg_color=("#C41E3A", "#FF6B6B"),
                        hover_color=("#A01828", "#E65A5A"),
                        width=130,
                    )
                    delete_btn.pack(side="left")
            else:
                no_msg = "💬 No complaints match your search" if _comp_filter["term"] or _comp_filter["status"] != "All" else "💬 No complaints found"
                ctk.CTkLabel(scrollable, text=no_msg, font=("Arial", 15), text_color=("gray50", "gray60")).pack(pady=40)

        def _do_comp_search():
            _comp_filter["term"] = search_entry_c.get()
            _comp_filter["status"] = status_filter_c.get()
            refresh_complaints(0)

        def _do_comp_clear():
            search_entry_c.delete(0, "end")
            status_filter_c.set("All")
            _comp_filter["term"] = ""
            _comp_filter["status"] = "All"
            refresh_complaints(0)

        search_btn_c.configure(command=_do_comp_search)
        clear_btn_c.configure(command=_do_comp_clear)
        search_entry_c.bind("<Return>", lambda _e: _do_comp_search())

        def handle_flag_complaint(complaint_id, current_status):
            try:
                new_status = 0 if current_status else 1
                self.update_complaint_status(complaint_id, new_status)
                refresh_complaints(_comp_page["n"])
            except Exception as e:
                print(f"Error flagging complaint: {e}")

        def handle_delete_complaint(complaint_id):
            try:
                self.delete_complaint(complaint_id)
                refresh_complaints(_comp_page["n"])
            except Exception as e:
                print(f"Error deleting complaint: {e}")

        refresh_complaints(0)

    view_complaint_button.configure(command=setup_view_complaint_popup)
