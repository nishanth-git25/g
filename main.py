from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dateutil import parser
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvoiceRequest(BaseModel):
    invoice_text: str


def find(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def money(value):
    if value is None:
        return None
    value = value.replace(",", "")
    try:
        return float(value)
    except:
        return None


@app.post("/extract")
def extract(data: InvoiceRequest):

    text = data.invoice_text

    invoice_no = find(
    r"(?:Invoice\s*(?:No|Number|#)|Inv\s*No|Bill\s*No)\s*[:#]?\s*([A-Za-z0-9\-\/]+)",
    text
    )

    vendor = find(
        r"Vendor[:\s]*(.+)",
        text
    )

    date_text = find(
        r"Date[:\s]*([^\n\r]+)",
        text
    )

    if date_text:
        try:
            date = parser.parse(date_text).date().isoformat()
        except:
            date = None
    else:
        date = None

    amount = money(
        find(
            r"Subtotal[:\s]*Rs\.?\s*([\d,]+\.\d+)",
            text
        )
    )

    tax = money(
        find(
            r"(?:GST|Tax).*?Rs\.?\s*([\d,]+\.\d+)",
            text
        )
    )

    return {
        "invoice_no": invoice_no,
        "date": date,
        "vendor": vendor,
        "amount": amount,
        "tax": tax,
        "currency": "INR"
    }