EMAIL_SUBJECT_TEMPLATE = "{market} Strategy Scan - {stage} - {run_date}"

EMAIL_BODY_TEMPLATE = """Hello,

Attached are the generated strategy CSV files.

Market: {market}
Stage: {stage}
Date: {run_date}

Regards,
Algo Trading Scanner V2
"""