import os
import shutil
import stat
import json
import zipfile

REPORT_ROOT = r"pbi\GreenPilotProject.Report"
REPORT_DEF_DIR = os.path.join(REPORT_ROOT, "definition")
PAGES_DIR = os.path.join(REPORT_DEF_DIR, "pages")
PBIX_FILE = "GreenPilotProjectReport.pbix"

def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def make_projection_measure(entity, prop, active=False):
    d = {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": entity}},
                "Property": prop
            }
        },
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop
    }
    if active:
        d["active"] = True
    return d

def make_measure_color_expr(entity, prop):
    return {
        "solid": {
            "color": {
                "expr": {
                    "Measure": {
                        "Expression": {"SourceRef": {"Entity": entity}},
                        "Property": prop
                    }
                }
            }
        }
    }

def make_literal_color_expr(hex_color):
    return {
        "solid": {
            "color": {
                "expr": {
                    "Literal": {
                        "Value": f"'{hex_color}'"
                    }
                }
            }
        }
    }

def make_cell_font_color(metadata_ref, color_measure_prop, back_color_hex=None):
    props = {
        "fontColor": make_measure_color_expr("_Measures", color_measure_prop)
    }
    if back_color_hex:
        props["backColor"] = make_literal_color_expr(back_color_hex)
    return {
        "selector": {"metadata": metadata_ref},
        "properties": props
    }

def make_cell_databars(metadata_ref, pos_hex="#15803D", neg_hex="#BE123C", axis_hex="#94A3B8", color_measure_prop=None):
    props = {
        "dataBars": {
            "positiveColor": make_literal_color_expr(pos_hex),
            "negativeColor": make_literal_color_expr(neg_hex),
            "axisColor": make_literal_color_expr(axis_hex),
            "reverseDirection": {"expr": {"Literal": {"Value": "false"}}},
            "hideText": {"expr": {"Literal": {"Value": "false"}}}
        }
    }
    if color_measure_prop:
        props["fontColor"] = make_measure_color_expr("_Measures", color_measure_prop)
    return {
        "selector": {"metadata": metadata_ref},
        "properties": props
    }

def make_projection_column(entity, prop, active=False):
    d = {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": entity}},
                "Property": prop
            }
        },
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop
    }
    if active:
        d["active"] = True
    return d

def write_visual(page_folder, vname, visual_dict, x, y, w, h, z, tab_order):
    vdir = os.path.join(page_folder, "visuals", vname)
    os.makedirs(vdir, exist_ok=True)
    vfile = os.path.join(vdir, "visual.json")
    payload = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.14.0/schema.json",
        "name": vname,
        "position": {
            "x": int(x),
            "y": int(y),
            "z": int(z),
            "height": int(h),
            "width": int(w),
            "tabOrder": int(tab_order)
        },
        "visual": visual_dict
    }
    with open(vfile, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

def prepare_page(pid, display_name):
    pdir = os.path.join(PAGES_DIR, pid)
    vroot = os.path.join(pdir, "visuals")
    if os.path.exists(vroot):
        try:
            shutil.rmtree(vroot, onexc=remove_readonly)
        except Exception:
            pass
    os.makedirs(vroot, exist_ok=True)
    with open(os.path.join(pdir, "page.json"), "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": pid,
            "displayName": display_name,
            "displayOption": "FitToPage",
            "height": 1080,
            "width": 1920
        }, f, indent=2)
    return pdir

def repack_pbix():
    if not os.path.exists(PBIX_FILE):
        print(f"[INFO] {PBIX_FILE} not found; skipping pbix repack.")
        return

    tmp_pbix = PBIX_FILE + ".tmp"
    with zipfile.ZipFile(PBIX_FILE, "r") as zin, zipfile.ZipFile(tmp_pbix, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        # 1. Copy non-Report entries from existing PBIX
        for item in zin.infolist():
            if not item.filename.startswith("Report/"):
                zout.writestr(item, zin.read(item.filename))

        # 2. Add all updated files from pbi/GreenPilotProject.Report
        for root, _, files in os.walk(REPORT_ROOT):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, REPORT_ROOT).replace("\\", "/")
                # Skip .pbi and .platform internal files
                if rel_path.startswith(".pbi/") or rel_path.startswith(".platform"):
                    continue
                zip_path = f"Report/{rel_path}"
                zout.write(full_path, zip_path)

    shutil.move(tmp_pbix, PBIX_FILE)
    print(f"[OK] Synchronized and repacked {PBIX_FILE} with updated PBIR pages!")

def build_pages():
    pages_meta = []

    # =========================================================================
    # PAGE 1: Executive EVM Scorecard & S-Curve
    # =========================================================================
    p1_id = "08f1eedb79c476b139b9"
    p1_dir = prepare_page(p1_id, "Executive EVM Scorecard & S-Curve")
    pages_meta.append(p1_id)

    # Header / Filter: Project Slicer
    slicer_proj_dict = {
        "visualType": "slicer",
        "query": {
            "queryState": {
                "Values": {"projections": [make_projection_column("Dim_Project", "project_id", active=True)]}
            }
        }
    }
    write_visual(p1_dir, "p1_slicer_project", slicer_proj_dict, 40, 15, 200, 120, 500, 500)

    # KPI Cards (Top): BAC, AC, EV, CPI, SPI, Physical Progress %
    top_kpis = [
        ("p1_kpi_bac", "_Measures", "Budget at Completion (BAC)", 255, 15, 255, 120, None),
        ("p1_kpi_ac", "_Measures", "Actual Cost (AC)", 525, 15, 255, 120, "CV Color RAG"),
        ("p1_kpi_ev", "_Measures", "Earned Value (EV)", 795, 15, 255, 120, None),
        ("p1_kpi_cpi", "_Measures", "Cost Performance Index (CPI)", 1065, 15, 255, 120, "CPI Color RAG"),
        ("p1_kpi_spi", "_Measures", "Schedule Performance Index (SPI)", 1335, 15, 255, 120, "SPI Color RAG"),
        ("p1_kpi_prog", "_Measures", "Physical Progress % (Current)", 1605, 15, 275, 120, "SPI Color RAG"),
    ]
    for idx, (vname, ent, prop, x, y, w, h, color_measure) in enumerate(top_kpis):
        vdict = {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {"projections": [make_projection_measure(ent, prop, active=True)]}
                }
            }
        }
        if color_measure:
            vdict["objects"] = {
                "labels": [
                    {
                        "properties": {
                            "color": make_measure_color_expr("_Measures", color_measure)
                        }
                    }
                ]
            }
        write_visual(p1_dir, vname, vdict, x, y, w, h, 1000 + idx * 100, (idx + 1) * 1000)

    # Visual 1 (Main Left): Line and Clustered Column Chart (S-Curve)
    scurve_dict = {
        "visualType": "lineClusteredColumnComboChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Dim_Date", "Period", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "Status Date Dynamic Line", active=True)]},
                "Y2": {
                    "projections": [
                        make_projection_measure("_Measures", "Planned Value Cumulative (PV S-Curve)", active=True),
                        make_projection_measure("_Measures", "Actual Cost Cumulative (AC S-Curve)", active=True),
                        make_projection_measure("_Measures", "Earned Value Cumulative (EV S-Curve)", active=True)
                    ]
                }
            }
        }
    }
    write_visual(p1_dir, "p1_scurve_combo", scurve_dict, 40, 150, 1060, 905, 2000, 7000)

    # Visual 2 (Main Right): Summary Matrix with Dynamic RAG & In-Cell Conditional Bar Lengths
    matrix_dict = {
        "visualType": "pivotTable",
        "query": {
            "queryState": {
                "Rows": {
                    "projections": [
                        make_projection_column("Dim_WBS", "wbs_id", active=True),
                        make_projection_column("Dim_WBS", "wbs_name", active=True)
                    ]
                },
                "Values": {
                    "projections": [
                        make_projection_measure("_Measures", "Budget at Completion (BAC)", active=True),
                        make_projection_measure("_Measures", "Planned Value (PV)", active=True),
                        make_projection_measure("_Measures", "Actual Cost (AC)", active=True),
                        make_projection_measure("_Measures", "Budget Consumption Bar", active=True),
                        make_projection_measure("_Measures", "Earned Value (EV)", active=True),
                        make_projection_measure("_Measures", "Cost Variance (CV)", active=True),
                        make_projection_measure("_Measures", "Cost Variance Bar", active=True),
                        make_projection_measure("_Measures", "Cost Performance Index (CPI)", active=True),
                        make_projection_measure("_Measures", "CPI Status RAG", active=True),
                        make_projection_measure("_Measures", "Schedule Performance Index (SPI)", active=True),
                        make_projection_measure("_Measures", "SPI Status RAG", active=True),
                        make_projection_measure("_Measures", "Physical Progress Bar", active=True)
                    ]
                }
            }
        },
        "objects": {
            "cellElements": [
                make_cell_font_color("_Measures.Budget Consumption Bar", "CV Color RAG"),
                make_cell_databars("_Measures.Cost Variance (CV)", pos_hex="#15803D", neg_hex="#BE123C", color_measure_prop="CV Color RAG"),
                make_cell_font_color("_Measures.Cost Variance Bar", "CV Color RAG"),
                make_cell_font_color("_Measures.Cost Performance Index (CPI)", "CPI Color RAG"),
                make_cell_font_color("_Measures.CPI Status RAG", "CPI Color RAG"),
                make_cell_font_color("_Measures.Schedule Performance Index (SPI)", "SPI Color RAG"),
                make_cell_font_color("_Measures.SPI Status RAG", "SPI Color RAG"),
                make_cell_font_color("_Measures.Physical Progress Bar", "SPI Color RAG")
            ]
        }
    }
    write_visual(p1_dir, "p1_wbs_matrix", matrix_dict, 1120, 150, 760, 905, 2100, 8000)

    # =========================================================================
    # PAGE 2: Root Cause & Variance Driver Matrix
    # =========================================================================
    p2_id = "11111111111111111112"
    p2_dir = prepare_page(p2_id, "Root Cause & Variance Driver Matrix")
    pages_meta.append(p2_id)

    # Visual 1 (Top Left): Clustered Bar Chart (Cost Variance by WBS) with Dynamic RAG Bar Fill
    decomp_dict = {
        "visualType": "clusteredBarChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Dim_WBS", "wbs_name", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "Cost Variance (CV)", active=True)]}
            }
        },
        "objects": {
            "dataPoint": [
                {
                    "properties": {
                        "fill": make_measure_color_expr("_Measures", "CV Color RAG")
                    }
                }
            ]
        }
    }
    write_visual(p2_dir, "p2_decomp_tree", decomp_dict, 40, 20, 1080, 500, 1000, 1000)

    # Visual 2 (Top Right): Diagnostic & Action Card with Overall RAG Badge
    diag_card_dict = {
        "visualType": "multiRowCard",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        make_projection_measure("_Measures", "Overall Project Health RAG", active=True),
                        make_projection_measure("_Measures", "Root Cause Primary Diagnosis", active=True),
                        make_projection_measure("_Measures", "Root Cause Driver Decomposition", active=True)
                    ]
                }
            }
        }
    }
    write_visual(p2_dir, "p2_diag_card", diag_card_dict, 1140, 20, 740, 500, 1100, 2000)

    # Visual 3 (Bottom Left): Scatter Plot (CPI vs. SPI by WBS)
    scatter_dict = {
        "visualType": "scatterChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Dim_WBS", "wbs_name", active=True)]},
                "X": {"projections": [make_projection_measure("_Measures", "Schedule Performance Index (SPI)", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "Cost Performance Index (CPI)", active=True)]},
                "Size": {"projections": [make_projection_measure("_Measures", "Actual Cost (AC)", active=True)]}
            }
        }
    }
    write_visual(p2_dir, "p2_scatter_wbs", scatter_dict, 40, 540, 880, 510, 1200, 3000)

    # Visual 4 (Bottom Right): Waterfall Chart (Variance Bridge by Cost Element)
    waterfall_dict = {
        "visualType": "waterfallChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Dim_CostElement", "cost_element_name", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "Cost Variance (CV)", active=True)]}
            }
        }
    }
    write_visual(p2_dir, "p2_waterfall_ce", waterfall_dict, 940, 540, 940, 510, 1300, 4000)

    # =========================================================================
    # PAGE 3: Procurement & Commitment Exposure
    # =========================================================================
    p3_id = "22222222222222222223"
    p3_dir = prepare_page(p3_id, "Procurement & Commitment Exposure")
    pages_meta.append(p3_id)

    # Top Cards: Total PO, Invoiced AP, Open Commitments, Open %
    po_cards = [
        ("p3_kpi_po_total", "_Measures", "PO Amount NOK", 40, 20, 440, 140, None),
        ("p3_kpi_po_inv", "_Measures", "PO Invoiced NOK", 500, 20, 440, 140, None),
        ("p3_kpi_po_open", "_Measures", "PO Open Commitment NOK", 960, 20, 440, 140, "PO Commitment Color RAG"),
        ("p3_kpi_po_rate", "_Measures", "PO Open Commitment %", 1420, 20, 460, 140, "PO Commitment Color RAG")
    ]
    for idx, (vname, ent, prop, x, y, w, h, color_measure) in enumerate(po_cards):
        vdict = {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {"projections": [make_projection_measure(ent, prop, active=True)]}
                }
            }
        }
        if color_measure:
            vdict["objects"] = {
                "labels": [
                    {
                        "properties": {
                            "color": make_measure_color_expr("_Measures", color_measure)
                        }
                    }
                ]
            }
        write_visual(p3_dir, vname, vdict, x, y, w, h, 1000 + idx * 100, (idx + 1) * 1000)

    # Visual 2: Table of Top Exposed Vendors with RAG & Conditional Bar Length (ALL projections active=True!)
    vendor_table_dict = {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        make_projection_column("Dim_Vendor", "vendor_name", active=True),
                        make_projection_column("Fact_PurchaseOrders", "currency", active=True),
                        make_projection_measure("_Measures", "PO Amount NOK", active=True),
                        make_projection_measure("_Measures", "PO Invoiced NOK", active=True),
                        make_projection_measure("_Measures", "PO Open Commitment NOK", active=True),
                        make_projection_measure("_Measures", "PO Commitment Exposure Bar", active=True),
                        make_projection_measure("_Measures", "PO Commitment Exposure RAG", active=True),
                        make_projection_column("Fact_PurchaseOrders", "po_status", active=True)
                    ]
                }
            }
        },
        "objects": {
            "cellElements": [
                make_cell_databars("_Measures.PO Open Commitment NOK", pos_hex="#D97706", neg_hex="#BE123C", color_measure_prop="PO Commitment Color RAG"),
                make_cell_font_color("_Measures.PO Commitment Exposure Bar", "PO Commitment Color RAG"),
                make_cell_font_color("_Measures.PO Commitment Exposure RAG", "PO Commitment Color RAG")
            ]
        }
    }
    write_visual(p3_dir, "p3_vendor_table", vendor_table_dict, 40, 180, 1260, 870, 2000, 5000)

    # Visual 3: Currency Exposure Donut Chart
    donut_currency_dict = {
        "visualType": "donutChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Fact_PurchaseOrders", "currency", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "PO Amount NOK", active=True)]}
            }
        }
    }
    write_visual(p3_dir, "p3_currency_donut", donut_currency_dict, 1320, 180, 560, 870, 2100, 6000)

    # =========================================================================
    # PAGE 4: IFRS / IAS 38 Accounting & AuC Capitalization
    # =========================================================================
    p4_id = "33333333333333333334"
    p4_dir = prepare_page(p4_id, "IFRS / IAS 38 Accounting & AuC Capitalization")
    pages_meta.append(p4_id)

    # Top KPI Cards for IFRS
    ifrs_kpis = [
        ("p4_kpi_total_ac", "_Measures", "Actual Cost (AC)", 40, 20, 440, 130, "CV Color RAG"),
        ("p4_kpi_auc", "_Measures", "Actual Cost Capitalized (AuC)", 500, 20, 440, 130, None),
        ("p4_kpi_pnl", "_Measures", "Actual Cost Expensed (P&L)", 960, 20, 440, 130, None),
        ("p4_kpi_rate", "_Measures", "Capitalization Rate %", 1420, 20, 460, 130, "AuC Capitalization Color RAG")
    ]
    for idx, (vname, ent, prop, x, y, w, h, color_measure) in enumerate(ifrs_kpis):
        vdict = {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {"projections": [make_projection_measure(ent, prop, active=True)]}
                }
            }
        }
        if color_measure:
            vdict["objects"] = {
                "labels": [
                    {
                        "properties": {
                            "color": make_measure_color_expr("_Measures", color_measure)
                        }
                    }
                ]
            }
        write_visual(p4_dir, vname, vdict, x, y, w, h, 1000 + idx * 100, (idx + 1) * 1000)

    # Visual 1 (Left): Donut split of AuC vs P&L
    auc_donut_dict = {
        "visualType": "donutChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Dim_WBS", "accounting_bucket", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "Actual Cost (AC)", active=True)]}
            }
        }
    }
    write_visual(p4_dir, "p4_auc_donut", auc_donut_dict, 40, 170, 600, 540, 2000, 5000)

    # Visual 2 (Right): Matrix by WBS and Accounting Treatment with RAG & Conditional Bar
    ifrs_matrix_dict = {
        "visualType": "pivotTable",
        "query": {
            "queryState": {
                "Rows": {
                    "projections": [
                        make_projection_column("Dim_WBS", "wbs_id", active=True),
                        make_projection_column("Dim_WBS", "wbs_name", active=True),
                        make_projection_column("Dim_WBS", "ias38_phase", active=True)
                    ]
                },
                "Values": {
                    "projections": [
                        make_projection_measure("_Measures", "Actual Cost (AC)", active=True),
                        make_projection_measure("_Measures", "Actual Cost Capitalized (AuC)", active=True),
                        make_projection_measure("_Measures", "Actual Cost Expensed (P&L)", active=True),
                        make_projection_measure("_Measures", "Capitalization Rate %", active=True),
                        make_projection_measure("_Measures", "AuC Capitalization Bar", active=True),
                        make_projection_measure("_Measures", "AuC Capitalization Rate RAG", active=True)
                    ]
                }
            }
        },
        "objects": {
            "cellElements": [
                make_cell_databars("_Measures.Capitalization Rate %", pos_hex="#0284C7", neg_hex="#BE123C", color_measure_prop="AuC Capitalization Color RAG"),
                make_cell_font_color("_Measures.AuC Capitalization Bar", "AuC Capitalization Color RAG"),
                make_cell_font_color("_Measures.AuC Capitalization Rate RAG", "AuC Capitalization Color RAG")
            ]
        }
    }
    write_visual(p4_dir, "p4_ifrs_matrix", ifrs_matrix_dict, 660, 170, 1220, 540, 2100, 6000)

    # Visual 3 (Bottom): IAS 36 Impairment Callout Warning Card
    impairment_card_dict = {
        "visualType": "card",
        "query": {
            "queryState": {
                "Values": {"projections": [make_projection_measure("_Measures", "IAS 36 Impairment Callout", active=True)]}
            }
        },
        "objects": {
            "labels": [
                {
                    "properties": {
                        "color": make_measure_color_expr("_Measures", "AuC Capitalization Color RAG")
                    }
                }
            ]
        }
    }
    write_visual(p4_dir, "p4_impairment_callout", impairment_card_dict, 40, 730, 1840, 320, 2200, 7000)

    # =========================================================================
    # PAGE 5: Prescriptive Controller Action Panel
    # =========================================================================
    p5_id = "44444444444444444445"
    p5_dir = prepare_page(p5_id, "Prescriptive Controller Action Panel")
    pages_meta.append(p5_id)

    # Visual 1 (Top Left / Full Top): Large Action Board
    action_board_dict = {
        "visualType": "card",
        "query": {
            "queryState": {
                "Values": {"projections": [make_projection_measure("_Measures", "Prescriptive Controller Actions", active=True)]}
            }
        }
    }
    write_visual(p5_dir, "p5_action_board", action_board_dict, 40, 20, 1840, 420, 1000, 1000)

    # Visual 2 (Bottom Left): Open Change Order Backlog Table with RAG & Conditional Bar Length
    co_table_dict = {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        make_projection_column("Fact_ChangeOrders", "change_order_id", active=True),
                        make_projection_column("Fact_ChangeOrders", "wbs_id", active=True),
                        make_projection_column("Fact_ChangeOrders", "status", active=True),
                        make_projection_measure("_Measures", "Change Order Status RAG", active=True),
                        make_projection_column("Fact_ChangeOrders", "requested_amount_nok", active=True),
                        make_projection_column("Fact_ChangeOrders", "approved_amount_nok", active=True),
                        make_projection_measure("_Measures", "Change Order Exposure Bar", active=True)
                    ]
                }
            }
        },
        "objects": {
            "cellElements": [
                make_cell_font_color("_Measures.Change Order Status RAG", "Change Order Status Color RAG"),
                make_cell_font_color("_Measures.Change Order Exposure Bar", "Change Order Status Color RAG")
            ]
        }
    }
    write_visual(p5_dir, "p5_co_table", co_table_dict, 40, 460, 890, 590, 1100, 2000)

    # Visual 3 (Bottom Right): Remaining Activities Audit with RAG & In-Cell Activity Progress Bar
    rem_act_dict = {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        make_projection_column("Dim_Activity", "activity_id", active=True),
                        make_projection_column("Dim_Activity", "activity_name", active=True),
                        make_projection_column("Dim_Activity", "wbs_id", active=True),
                        make_projection_column("Dim_Activity", "status", active=True),
                        make_projection_measure("_Measures", "Activity Status RAG", active=True),
                        make_projection_measure("_Measures", "Activity Progress Bar", active=True),
                        make_projection_column("Dim_Activity", "progress_pct", active=True),
                        make_projection_column("Dim_Activity", "planned_finish", active=True)
                    ]
                }
            }
        },
        "objects": {
            "cellElements": [
                make_cell_font_color("_Measures.Activity Status RAG", "Activity Status Color RAG"),
                make_cell_font_color("_Measures.Activity Progress Bar", "Activity Status Color RAG")
            ]
        }
    }
    write_visual(p5_dir, "p5_remaining_activities", rem_act_dict, 950, 460, 930, 590, 1200, 3000)

    # =========================================================================
    # PAGE 6: Likviditet & Koststeder Fiskå
    # =========================================================================
    p6_id = "55555555555555555556"
    p6_dir = prepare_page(p6_id, "Likviditet & Koststeder Fiskå")
    pages_meta.append(p6_id)

    # Top Cards: Total Cash Outflow, Enova Grant In, Cumulative Net Cash Flow, Open PO Commitments
    cf_cards = [
        ("p6_kpi_cash_out", "_Measures", "Total Cash Outflow NOK", 40, 20, 440, 130, None),
        ("p6_kpi_enova_in", "_Measures", "Enova Grant Cash In NOK", 500, 20, 440, 130, None),
        ("p6_kpi_cum_net_cf", "_Measures", "Cumulative Net Cash Flow NOK", 960, 20, 440, 130, None),
        ("p6_kpi_open_po", "_Measures", "PO Open Commitment NOK", 1420, 20, 460, 130, "PO Commitment Color RAG")
    ]
    for idx, (vname, ent, prop, x, y, w, h, color_measure) in enumerate(cf_cards):
        vdict = {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {"projections": [make_projection_measure(ent, prop, active=True)]}
                }
            }
        }
        if color_measure:
            vdict["objects"] = {
                "labels": [
                    {
                        "properties": {
                            "color": make_measure_color_expr("_Measures", color_measure)
                        }
                    }
                ]
            }
        write_visual(p6_dir, vname, vdict, x, y, w, h, 1000 + idx * 100, (idx + 1) * 1000)

    # Visual 2 (Middle Left): Cash Flow Bridge & Cumulative Working Capital Combo Chart
    cf_combo_dict = {
        "visualType": "lineClusteredColumnComboChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Dim_Date", "Date", active=True)]},
                "ColumnY": {
                    "projections": [
                        make_projection_measure("_Measures", "Supplier AP Paid NOK", active=True),
                        make_projection_measure("_Measures", "Internal Payroll Paid NOK", active=True),
                        make_projection_measure("_Measures", "Enova Grant Cash In NOK", active=True)
                    ]
                },
                "LineY": {
                    "projections": [
                        make_projection_measure("_Measures", "Cumulative Net Cash Flow NOK", active=True)
                    ]
                }
            }
        }
    }
    write_visual(p6_dir, "p6_cashflow_combo", cf_combo_dict, 40, 170, 960, 430, 2000, 5000)

    # Visual 3 (Middle Right): Elkem Fiskå Cost Center Matrix with Conditional Bar Length
    cc_matrix_dict = {
        "visualType": "pivotTable",
        "query": {
            "queryState": {
                "Rows": {
                    "projections": [
                        make_projection_column("Dim_CostCenter", "cost_center_name", active=True),
                        make_projection_column("Dim_CostCenter", "department", active=True)
                    ]
                },
                "Values": {
                    "projections": [
                        make_projection_measure("_Measures", "Faktiske Timer Koststed", active=True),
                        make_projection_measure("_Measures", "Personalkostnad Koststed NOK", active=True),
                        make_projection_measure("_Measures", "Andel Timer Koststed %", active=True),
                        make_projection_measure("_Measures", "Koststed Timer Bar", active=True)
                    ]
                }
            }
        },
        "objects": {
            "cellElements": [
                make_cell_databars("_Measures.Andel Timer Koststed %", pos_hex="#0284C7", neg_hex="#BE123C")
            ]
        }
    }
    write_visual(p6_dir, "p6_costcenter_matrix", cc_matrix_dict, 1020, 170, 860, 430, 2100, 6000)

    # Visual 4 (Bottom Full Width): Monthly Early Warning Log with Dynamic RAG & PO Exposure Bar
    ew_table_dict = {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        make_projection_column("Fact_MonthlyEarlyWarnings", "period", active=True),
                        make_projection_measure("_Measures", "Early Warning Status RAG", active=True),
                        make_projection_measure("_Measures", "Early Warning PO Exposure Bar", active=True),
                        make_projection_column("Fact_MonthlyEarlyWarnings", "cpi", active=True),
                        make_projection_column("Fact_MonthlyEarlyWarnings", "spi", active=True),
                        make_projection_column("Fact_MonthlyEarlyWarnings", "projected_eac_nok", active=True),
                        make_projection_column("Fact_MonthlyEarlyWarnings", "controller_action_required", active=True)
                    ]
                }
            }
        },
        "objects": {
            "cellElements": [
                make_cell_font_color("_Measures.Early Warning Status RAG", "Early Warning Color RAG"),
                make_cell_font_color("_Measures.Early Warning PO Exposure Bar", "Early Warning Color RAG")
            ]
        }
    }
    write_visual(p6_dir, "p6_early_warning_table", ew_table_dict, 40, 620, 1840, 430, 2200, 7000)

    # Update pages.json
    pages_json_path = os.path.join(PAGES_DIR, "pages.json")
    with open(pages_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
            "pageOrder": pages_meta,
            "activePageName": p1_id
        }, f, indent=2)

    print(f"Successfully generated {len(pages_meta)} clean pages in {PAGES_DIR}!")

    # Repack PBIX
    repack_pbix()

if __name__ == "__main__":
    build_pages()
