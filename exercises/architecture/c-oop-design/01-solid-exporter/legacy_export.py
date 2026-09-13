"""The 'before' version — read it, don't edit it. What would you have to change to add Excel, or upload to S3?"""

import json


def export(applications, format, path):
    if format == "csv":
        lines = ["company,role,status,applied_on"]
        for a in applications:
            lines.append(f"{a['company']},{a['role']},{a['status']},{a['applied_on'] or ''}")  # 🐛 commas in names break it
        content = "\n".join(lines)
    elif format == "json":
        content = json.dumps([{**a, "applied_on": str(a["applied_on"])} for a in applications])  # 🐛 None becomes "None"
    elif format == "md":
        content = "| Company | Role |\n" + "\n".join(f"| {a['company']} | {a['role']} |" for a in applications)
    else:
        raise ValueError("unknown format")
    with open(path, "w") as f:  # rendering and saving tangled together
        f.write(content)
