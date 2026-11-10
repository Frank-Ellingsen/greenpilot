import os
import re
import uuid

TMDL_FILE = r"pbi\GreenPilotProject.SemanticModel\definition\tables\_Measures.tmdl"

NEW_MEASURES = [
    # ---------------------------------------------------------
    # 09 DYNAMISK RAG FORMATERING (FARGE & STATUS)
    # ---------------------------------------------------------
    {
        "name": "CPI Status RAG",
        "dax": """VAR V = [Cost Performance Index (CPI)]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( V ), BLANK (),
    V >= 0.95, "🟢 Green (" & FORMAT ( V, "0.00" ) & ")",
    V >= 0.85, "🟡 Amber (" & FORMAT ( V, "0.00" ) & ")",
    "🔴 Red (" & FORMAT ( V, "0.00" ) & ")"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "CPI Color RAG",
        "dax": """VAR V = [Cost Performance Index (CPI)]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( V ), BLANK (),
    V >= 0.95, "#15803D",
    V >= 0.85, "#D97706",
    "#BE123C"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "SPI Status RAG",
        "dax": """VAR V = [Schedule Performance Index (SPI)]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( V ), BLANK (),
    V >= 0.95, "🟢 Green (" & FORMAT ( V, "0.00" ) & ")",
    V >= 0.85, "🟡 Amber (" & FORMAT ( V, "0.00" ) & ")",
    "🔴 Red (" & FORMAT ( V, "0.00" ) & ")"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "SPI Color RAG",
        "dax": """VAR V = [Schedule Performance Index (SPI)]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( V ), BLANK (),
    V >= 0.95, "#15803D",
    V >= 0.85, "#D97706",
    "#BE123C"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "CV Status RAG",
        "dax": """VAR V = [Cost Variance (CV)]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( V ), BLANK (),
    V >= 0, "🟢 On Budget (+" & FORMAT ( V / 1e6, "0.00" ) & "M)",
    V >= -1000000, "🟡 Minor Overrun (" & FORMAT ( V / 1e6, "0.00" ) & "M)",
    "🔴 Critical Overrun (" & FORMAT ( V / 1e6, "0.00" ) & "M)"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "CV Color RAG",
        "dax": """VAR V = [Cost Variance (CV)]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( V ), BLANK (),
    V >= 0, "#15803D",
    V >= -1000000, "#D97706",
    "#BE123C"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "SV Status RAG",
        "dax": """VAR V = [Schedule Variance (SV)]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( V ), BLANK (),
    V >= 0, "🟢 Ahead (+" & FORMAT ( V / 1e6, "0.00" ) & "M)",
    V >= -500000, "🟡 Minor Delay (" & FORMAT ( V / 1e6, "0.00" ) & "M)",
    "🔴 Critical Delay (" & FORMAT ( V / 1e6, "0.00" ) & "M)"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "SV Color RAG",
        "dax": """VAR V = [Schedule Variance (SV)]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( V ), BLANK (),
    V >= 0, "#15803D",
    V >= -500000, "#D97706",
    "#BE123C"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "PO Commitment Exposure RAG",
        "dax": """VAR OpenPO = [PO Open Commitment NOK]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( OpenPO ), BLANK (),
    OpenPO > 25000000, "🔴 High Exposure (>25M)",
    OpenPO > 10000000, "🟡 Moderate Exposure (10-25M)",
    "🟢 Controlled Exposure (<10M)"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "PO Commitment Color RAG",
        "dax": """VAR OpenPO = [PO Open Commitment NOK]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( OpenPO ), BLANK (),
    OpenPO > 25000000, "#BE123C",
    OpenPO > 10000000, "#D97706",
    "#15803D"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "AuC Capitalization Rate RAG",
        "dax": """VAR Rate = [Capitalization Rate %]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( Rate ), BLANK (),
    Rate > 0.80, "🔴 High Impairment Risk (>80%)",
    Rate > 0.60, "🟡 Elevated AuC (60-80%)",
    "🟢 Normal (<60%)"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "AuC Capitalization Color RAG",
        "dax": """VAR Rate = [Capitalization Rate %]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( Rate ), BLANK (),
    Rate > 0.80, "#BE123C",
    Rate > 0.60, "#D97706",
    "#15803D"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "Overall Project Health RAG",
        "dax": """VAR CPI = [Cost Performance Index (CPI)]
VAR SPI = [Schedule Performance Index (SPI)]
VAR OpenPO = [PO Open Commitment NOK]
RETURN
SWITCH (
    TRUE (),
    CPI < 0.80 || OpenPO > 25000000, "🔴 CRITICAL OVERRUN (CPI: " & FORMAT ( CPI, "0.00" ) & " | Open PO: " & FORMAT ( OpenPO / 1e6, "0.0" ) & "M NOK)",
    CPI < 0.95 || SPI < 0.95, "🟡 CAUTION (CPI: " & FORMAT ( CPI, "0.00" ) & " | SPI: " & FORMAT ( SPI, "0.00" ) & ")",
    "🟢 ON TRACK (CPI: " & FORMAT ( CPI, "0.00" ) & " | SPI: " & FORMAT ( SPI, "0.00" ) & ")"
)""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },
    {
        "name": "Overall Project Health Color RAG",
        "dax": """VAR CPI = [Cost Performance Index (CPI)]
VAR OpenPO = [PO Open Commitment NOK]
RETURN
IF ( CPI < 0.80 || OpenPO > 25000000, "#BE123C", IF ( CPI < 0.95, "#D97706", "#15803D" ) )""",
        "displayFolder": "09 DYNAMISK RAG FORMATERING",
        "formatString": None
    },

    # ---------------------------------------------------------
    # 10 BETINGET STOLPELENGDE (IN-CELL DATA BARS)
    # ---------------------------------------------------------
    {
        "name": "Cost Variance Bar",
        "dax": """VAR Val = [Cost Variance (CV)]
VAR MaxScale = 15000000
VAR BarMaxLen = 12
VAR Ratio = MIN ( 1.0, DIVIDE ( ABS ( Val ), MaxScale, 0 ) )
VAR BarLen = MAX ( 1, ROUND ( Ratio * BarMaxLen, 0 ) )
VAR BarStr = REPT ( "█", BarLen )
RETURN
IF (
    ISBLANK ( Val ),
    BLANK (),
    IF ( Val >= 0, "🟩 " & BarStr & " (+" & FORMAT ( Val / 1e6, "0.0" ) & "M)", "🟥 " & BarStr & " (" & FORMAT ( Val / 1e6, "0.0" ) & "M)" )
)""",
        "displayFolder": "10 BETINGET STOLPELENGDE",
        "formatString": None
    },
    {
        "name": "Physical Progress Bar",
        "dax": """VAR Pct = [Physical Progress % (Current)]
VAR BarMax = 10
VAR Filled = MIN ( BarMax, MAX ( 0, ROUND ( Pct * BarMax, 0 ) ) )
VAR Empty = BarMax - Filled
RETURN
IF ( ISBLANK ( Pct ), BLANK (), REPT ( "█", Filled ) & REPT ( "░", Empty ) & " " & FORMAT ( Pct, "0.0%" ) )""",
        "displayFolder": "10 BETINGET STOLPELENGDE",
        "formatString": None
    },
    {
        "name": "Activity Progress Bar",
        "dax": """VAR Pct = DIVIDE ( SELECTEDVALUE ( Dim_Activity[progress_pct], 0 ), 100, 0 )
VAR Filled = MIN ( 10, MAX ( 0, ROUND ( Pct * 10, 0 ) ) )
VAR Empty = 10 - Filled
RETURN
REPT ( "█", Filled ) & REPT ( "░", Empty ) & " " & FORMAT ( Pct, "0%" )""",
        "displayFolder": "10 BETINGET STOLPELENGDE",
        "formatString": None
    },
    {
        "name": "Budget Consumption Bar",
        "dax": """VAR BAC = [Budget at Completion (BAC)]
VAR AC = [Actual Cost (AC)]
VAR Ratio = DIVIDE ( AC, BAC, 0 )
VAR BarLen = MIN ( 15, MAX ( 1, ROUND ( Ratio * 4, 0 ) ) )
RETURN
IF (
    ISBLANK ( Ratio ) || BAC == 0,
    BLANK (),
    IF ( Ratio > 1.0, "🟥 " & REPT ( "■", BarLen ) & " " & FORMAT ( Ratio, "0.0%" ), "🟩 " & REPT ( "■", BarLen ) & " " & FORMAT ( Ratio, "0.0%" ) )
)""",
        "displayFolder": "10 BETINGET STOLPELENGDE",
        "formatString": None
    },
    {
        "name": "PO Commitment Exposure Bar",
        "dax": """VAR OpenPO = [PO Open Commitment NOK]
VAR TotalPO = [PO Amount NOK]
VAR Rate = DIVIDE ( OpenPO, TotalPO, 0 )
VAR Filled = MIN ( 10, MAX ( 0, ROUND ( Rate * 10, 0 ) ) )
VAR Empty = 10 - Filled
RETURN
IF ( ISBLANK ( OpenPO ) || TotalPO == 0, BLANK (), "🟧 " & REPT ( "■", Filled ) & REPT ( "□", Empty ) & " " & FORMAT ( Rate, "0.0%" ) )""",
        "displayFolder": "10 BETINGET STOLPELENGDE",
        "formatString": None
    },
    {
        "name": "AuC Capitalization Bar",
        "dax": """VAR Rate = [Capitalization Rate %]
VAR Filled = MIN ( 10, MAX ( 0, ROUND ( Rate * 10, 0 ) ) )
VAR Empty = 10 - Filled
RETURN
IF ( ISBLANK ( Rate ), BLANK (), "🟦 " & REPT ( "■", Filled ) & REPT ( "□", Empty ) & " " & FORMAT ( Rate, "0.0%" ) )""",
        "displayFolder": "10 BETINGET STOLPELENGDE",
        "formatString": None
    }
]

def update_tmdl():
    with open(TMDL_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split before column Value
    marker = "\tcolumn Value"
    if marker not in content:
        raise ValueError(f"Could not find marker '{marker}' in {TMDL_FILE}")

    head, tail = content.split(marker, 1)

    # Format new measures
    new_tmdl_blocks = []
    for m in NEW_MEASURES:
        # Check if already present
        pattern = rf"measure\s+'{re.escape(m['name'])}'"
        if re.search(pattern, head):
            print(f"Skipping existing measure: {m['name']}")
            continue

        lines = [f"\tmeasure '{m['name']}' ="]
        for dax_line in m['dax'].splitlines():
            lines.append(f"\t\t\t{dax_line}")
        if m.get('formatString'):
            lines.append(f"\t\tformatString: {m['formatString']}")
        if m.get('displayFolder'):
            lines.append(f"\t\tdisplayFolder: {m['displayFolder']}")
        lines.append(f"\t\tlineageTag: {uuid.uuid4()}")
        lines.append("")
        new_tmdl_blocks.append("\n".join(lines))

    if new_tmdl_blocks:
        head = head.rstrip() + "\n\n" + "\n".join(new_tmdl_blocks) + "\n"
        new_content = head + marker + tail
        with open(TMDL_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully added {len(new_tmdl_blocks)} measures to {TMDL_FILE}")
    else:
        print("No new measures to add.")

if __name__ == "__main__":
    update_tmdl()

