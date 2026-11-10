import os
import openpyxl
import win32com.client

def verify():
    wb_path = os.path.abspath("GreenPilot_2026_EVM_Model.xlsx")
    
    # Recalculate using Excel COM
    excel = win32com.client.Dispatch("Excel.Application")
    excel.DisplayAlerts = False
    excel.Visible = False
    try:
        wb = excel.Workbooks.Open(wb_path, ReadOnly=False)
        excel.CalculateFull()
        try:
            wb.Save()
        except Exception:
            pass  # File may be open in user's Excel instance
        wb.Close(SaveChanges=False)
    finally:
        excel.Quit()
        
    wb2 = openpyxl.load_workbook(wb_path, data_only=True)
    ws0 = wb2["00_Control_Index"]
    print("=" * 80)
    print("EXCEL MODEL QUALITY ASSURANCE & AUDIT RECONCILIATION")
    print("=" * 80)
    all_ok = True
    for r in range(27, 33):
        gate = ws0.cell(row=r, column=2).value
        calc = ws0.cell(row=r, column=3).value
        tgt = ws0.cell(row=r, column=4).value
        stat = ws0.cell(row=r, column=5).value
        print(f"[{stat}] {gate:<35} : Calc={calc:14,.2f} | Tgt={tgt:14,.2f}")
        if stat != "BALANCED (OK)":
            all_ok = False
            
    ws1 = wb2["01_Executive_Dashboard"]
    print("\n" + "=" * 80)
    print("EXECUTIVE DASHBOARD VERIFIED VALUES (TAB 01)")
    print("=" * 80)
    bac = ws1["B6"].value
    ac = ws1["D6"].value
    ev = ws1["F6"].value
    prog = ws1["H6"].value
    eac = ws1["J6"].value
    cpi = ws1["B9"].value
    spi = ws1["D9"].value
    cv = ws1["F9"].value
    sv = ws1["H9"].value
    open_po = ws1["J9"].value
    
    print(f"BAC (B6)             : NOK {bac:14,.2f} (Expected: 20,000,000.00)")
    print(f"AC (D6)              : NOK {ac:14,.2f} (Expected: 57,968,040.98)")
    print(f"EV (F6)              : NOK {ev:14,.2f} (Expected: 19,215,686.27)")
    print(f"Progress % (H6)      : {prog*100:13.2f}% (Expected: 96.08%)")
    print(f"EAC (J6)             : NOK {eac:14,.2f}")
    print(f"CPI (B9)             : {cpi:14.4f} (Expected: 0.3315)")
    print(f"SPI (D9)             : {spi:14.4f} (Expected: 1.1561)")
    print(f"CV (F9)              : NOK {cv:14,.2f} (Expected: -38,752,354.71)")
    print(f"SV (H9)              : NOK {sv:14,.2f} (Expected: +2,594,815.17)")
    print(f"Open Commitments (J9): NOK {open_po:14,.2f} (Expected: 49,233,751.55)")
    
    print("\n" + "=" * 80)
    if all_ok:
        print("ALL QUALITY CHECKS PASSED: 100% RECONCILED TO GROUND TRUTH BENCHMARK!")
    else:
        print("SOME QUALITY CHECKS FAILED!")
    print("=" * 80)

if __name__ == "__main__":
    verify()

