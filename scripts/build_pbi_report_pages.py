import os
import shutil
import stat
import json

REPORT_DEF_DIR = r"pbi\GreenPilotProject.Report\definition"
PAGES_DIR = os.path.join(REPORT_DEF_DIR, "pages")

def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def make_projection_measure(entity, prop):
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": entity}},
                "Property": prop
            }
        },
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop
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
            "x": float(x),
            "y": float(y),
            "z": int(z),
            "height": float(h),
            "width": float(w),
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

def build_pages():
    pages_meta = []

    # =========================================================================
    # PAGE 1: Executive EVM Scorecard & S-Curve
    # =========================================================================
    p1_id = "08f1eedb79c476b139b9"
    p1_dir = prepare_page(p1_id, "Executive EVM Scorecard & S-Curve")
    pages_meta.append(p1_id)

    # Header / Filter: Project Slicer & Cut-off Indicator
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
        ("p1_kpi_bac", "_Measures", "Budget at Completion (BAC)", 255, 15, 255, 120),
        ("p1_kpi_ac", "_Measures", "Actual Cost (AC)", 525, 15, 255, 120),
        ("p1_kpi_ev", "_Measures", "Earned Value (EV)", 795, 15, 255, 120),
        ("p1_kpi_cpi", "_Measures", "Cost Performance Index (CPI)", 1065, 15, 255, 120),
        ("p1_kpi_spi", "_Measures", "Schedule Performance Index (SPI)", 1335, 15, 255, 120),
        ("p1_kpi_prog", "_Measures", "Physical Progress % (Current)", 1605, 15, 275, 120),
    ]
    for idx, (vname, ent, prop, x, y, w, h) in enumerate(top_kpis):
        vdict = {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {"projections": [make_projection_measure(ent, prop)]}
                }
            }
        }
        write_visual(p1_dir, vname, vdict, x, y, w, h, 1000 + idx * 100, (idx + 1) * 1000)

    # Visual 1 (Main Left): Line and Clustered Column Chart (S-Curve)
    scurve_dict = {
        "visualType": "lineClusteredColumnComboChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Dim_Date", "Period", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "Status Date Dynamic Line")]},
                "Y2": {
                    "projections": [
                        make_projection_measure("_Measures", "Planned Value Cumulative (PV S-Curve)"),
                        make_projection_measure("_Measures", "Actual Cost Cumulative (AC S-Curve)"),
                        make_projection_measure("_Measures", "Earned Value Cumulative (EV S-Curve)")
                    ]
                }
            }
        }
    }
    write_visual(p1_dir, "p1_scurve_combo", scurve_dict, 40, 150, 1170, 905, 2000, 7000)

    # Visual 2 (Main Right): Summary Matrix showing WBS breakdown
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
                        make_projection_measure("_Measures", "Budget at Completion (BAC)"),
                        make_projection_measure("_Measures", "Planned Value (PV)"),
                        make_projection_measure("_Measures", "Actual Cost (AC)"),
                        make_projection_measure("_Measures", "Earned Value (EV)"),
                        make_projection_measure("_Measures", "Cost Variance (CV)"),
                        make_projection_measure("_Measures", "Cost Performance Index (CPI)")
                    ]
                }
            }
        }
    }
    write_visual(p1_dir, "p1_wbs_matrix", matrix_dict, 1225, 150, 655, 905, 2100, 8000)

    # =========================================================================
    # PAGE 2: Root Cause & Variance Driver Matrix
    # =========================================================================
    p2_id = "11111111111111111112"
    p2_dir = prepare_page(p2_id, "Root Cause & Variance Driver Matrix")
    pages_meta.append(p2_id)

    # Visual 1 (Top Left): Decomposition Tree (Nedbrytingstre)
    decomp_dict = {
        "visualType": "decompositionTree",
        "query": {
            "queryState": {
                "Analyze": {"projections": [make_projection_measure("_Measures", "Cost Variance (CV)")]},
                "Category": {
                    "projections": [
                        make_projection_column("Dim_WBS", "wbs_name", active=True),
                        make_projection_column("Dim_CostElement", "cost_element_name", active=True),
                        make_projection_column("Dim_Vendor", "vendor_name", active=True)
                    ]
                }
            }
        }
    }
    write_visual(p2_dir, "p2_decomp_tree", decomp_dict, 40, 20, 1080, 500, 1000, 1000)

    # Visual 2 (Top Right): Diagnostic & Action Card
    diag_card_dict = {
        "visualType": "cardVisual",
        "query": {
            "queryState": {
                "Data": {
                    "projections": [
                        make_projection_measure("_Measures", "Root Cause Primary Diagnosis"),
                        make_projection_measure("_Measures", "Root Cause Driver Decomposition")
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
                "X": {"projections": [make_projection_measure("_Measures", "Schedule Performance Index (SPI)")]},
                "Y": {"projections": [make_projection_measure("_Measures", "Cost Performance Index (CPI)")]},
                "Size": {"projections": [make_projection_measure("_Measures", "Actual Cost (AC)")]}
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
                "Y": {"projections": [make_projection_measure("_Measures", "Cost Variance (CV)")]}
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
        ("p3_kpi_po_total", "_Measures", "PO Amount NOK", 40, 20, 440, 140),
        ("p3_kpi_po_inv", "_Measures", "PO Invoiced NOK", 500, 20, 440, 140),
        ("p3_kpi_po_open", "_Measures", "PO Open Commitment NOK", 960, 20, 440, 140),
        ("p3_kpi_po_rate", "_Measures", "PO Open Commitment %", 1420, 20, 460, 140)
    ]
    for idx, (vname, ent, prop, x, y, w, h) in enumerate(po_cards):
        vdict = {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {"projections": [make_projection_measure(ent, prop)]}
                }
            }
        }
        write_visual(p3_dir, vname, vdict, x, y, w, h, 1000 + idx * 100, (idx + 1) * 1000)

    # Visual 2: Table of Top Exposed Vendors
    vendor_table_dict = {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        make_projection_column("Dim_Vendor", "vendor_name", active=True),
                        make_projection_column("Fact_PurchaseOrders", "currency", active=True),
                        make_projection_measure("_Measures", "PO Amount NOK"),
                        make_projection_measure("_Measures", "PO Invoiced NOK"),
                        make_projection_measure("_Measures", "PO Open Commitment NOK"),
                        make_projection_column("Fact_PurchaseOrders", "po_status", active=True)
                    ]
                }
            }
        }
    }
    write_visual(p3_dir, "p3_vendor_table", vendor_table_dict, 40, 180, 1260, 870, 2000, 5000)

    # Visual 3: Currency Exposure Donut Chart
    donut_currency_dict = {
        "visualType": "donutChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Fact_PurchaseOrders", "currency", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "PO Amount NOK")]}
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
        ("p4_kpi_total_ac", "_Measures", "Actual Cost (AC)", 40, 20, 440, 130),
        ("p4_kpi_auc", "_Measures", "Actual Cost Capitalized (AuC)", 500, 20, 440, 130),
        ("p4_kpi_pnl", "_Measures", "Actual Cost Expensed (P&L)", 960, 20, 440, 130),
        ("p4_kpi_rate", "_Measures", "Capitalization Rate %", 1420, 20, 460, 130)
    ]
    for idx, (vname, ent, prop, x, y, w, h) in enumerate(ifrs_kpis):
        vdict = {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {"projections": [make_projection_measure(ent, prop)]}
                }
            }
        }
        write_visual(p4_dir, vname, vdict, x, y, w, h, 1000 + idx * 100, (idx + 1) * 1000)

    # Visual 1 (Left): Donut / Column split of AuC vs P&L
    auc_donut_dict = {
        "visualType": "donutChart",
        "query": {
            "queryState": {
                "Category": {"projections": [make_projection_column("Dim_WBS", "accounting_bucket", active=True)]},
                "Y": {"projections": [make_projection_measure("_Measures", "Actual Cost (AC)")]}
            }
        }
    }
    write_visual(p4_dir, "p4_auc_donut", auc_donut_dict, 40, 170, 600, 540, 2000, 5000)

    # Visual 2 (Right): Matrix by WBS and Accounting Treatment
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
                        make_projection_measure("_Measures", "Actual Cost (AC)"),
                        make_projection_measure("_Measures", "Actual Cost Capitalized (AuC)"),
                        make_projection_measure("_Measures", "Actual Cost Expensed (P&L)"),
                        make_projection_measure("_Measures", "Capitalization Rate %")
                    ]
                }
            }
        }
    }
    write_visual(p4_dir, "p4_ifrs_matrix", ifrs_matrix_dict, 660, 170, 1220, 540, 2100, 6000)

    # Visual 3 (Bottom): IAS 36 Impairment Callout Warning Card
    impairment_card_dict = {
        "visualType": "cardVisual",
        "query": {
            "queryState": {
                "Data": {"projections": [make_projection_measure("_Measures", "IAS 36 Impairment Callout")]}
            }
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
        "visualType": "cardVisual",
        "query": {
            "queryState": {
                "Data": {"projections": [make_projection_measure("_Measures", "Prescriptive Controller Actions")]}
            }
        }
    }
    write_visual(p5_dir, "p5_action_board", action_board_dict, 40, 20, 1840, 420, 1000, 1000)

    # Visual 2 (Bottom Left): Open Change Order Backlog Table
    co_table_dict = {
        "visualType": "tableEx",
        "query": {
            "queryState": {
                "Values": {
                    "projections": [
                        make_projection_column("Fact_ChangeOrders", "change_order_id", active=True),
                        make_projection_column("Fact_ChangeOrders", "wbs_id", active=True),
                        make_projection_column("Fact_ChangeOrders", "status", active=True),
                        make_projection_column("Fact_ChangeOrders", "requested_amount_nok", active=True),
                        make_projection_column("Fact_ChangeOrders", "approved_amount_nok", active=True)
                    ]
                }
            }
        }
    }
    write_visual(p5_dir, "p5_co_table", co_table_dict, 40, 460, 890, 590, 1100, 2000)

    # Visual 3 (Bottom Right): Remaining Activities Audit (In Progress & Not Started)
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
                        make_projection_column("Dim_Activity", "progress_pct", active=True),
                        make_projection_column("Dim_Activity", "planned_finish", active=True)
                    ]
                }
            }
        }
    }
    write_visual(p5_dir, "p5_remaining_activities", rem_act_dict, 950, 460, 930, 590, 1200, 3000)

    # Update pages.json
    pages_json_path = os.path.join(PAGES_DIR, "pages.json")
    with open(pages_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
            "pageOrder": pages_meta,
            "activePageName": p1_id
        }, f, indent=2)

    print(f"Successfully generated {len(pages_meta)} clean pages in {PAGES_DIR}!")

if __name__ == "__main__":
    build_pages()
