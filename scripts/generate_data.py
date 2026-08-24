import random
import csv
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from faker import Faker

fake = Faker('en_IN')
random.seed(42)
Faker.seed(42)

COUNTERPARTIES = [
    "ABC ENTERPRISES", "XYZ CORPORATION", "GLOBAL TECH SOLUTIONS", "METRO RETAIL",
    "PRIME VENDORS", "STAR DISTRIBUTORS", "URBAN MERCHANTS", "CAPITAL TRADERS",
    "HORIZON IMPORTS", "NEXUS SERVICES", "VERTEX CONSULTING", "APEX LOGISTICS",
    "ZENITH MANUFACTURING", "ORBIT FINANCIAL", "MERIDIAN SUPPLIES"
]

BANK_DESCRIPTIONS = [
    "NEFT TRANSFER", "RTGS PAYMENT", "IMPS CREDIT", "UPI PAYMENT", "CHEQUE DEPOSIT",
    "ONLINE TRANSFER", "SALARY CREDIT", "VENDOR PAYMENT", "REFUND RECEIVED", "INTEREST CREDIT"
]

LEDGER_DESCRIPTIONS = [
    "INVOICE PAYMENT", "BILL SETTLEMENT", "ADVANCE RECEIVED", "REFUND PROCESSED",
    "EXPENSE REIMBURSEMENT", "SALES RECEIPT", "PURCHASE PAYMENT", "TAX PAYMENT"
]

PROCESSOR_DESCRIPTIONS = [
    "ONLINE PAYMENT", "CARD TRANSACTION", "WALLET PAYMENT", "NETBANKING",
    "UPI COLLECTION", "SUBSCRIPTION CHARGE", "MARKETPLACE SETTLEMENT"
]

DISCREPANCY_TYPES = [
    "clean_match", "amount_mismatch_fee", "amount_mismatch_rounding", "date_mismatch",
    "missing_ledger", "missing_bank", "duplicate_ledger", "reference_error",
    "currency_issue", "ambiguous", "processor_fee"
]

def generate_base_transaction(txn_id: int, base_date: date) -> Dict[str, Any]:
    counterparty = random.choice(COUNTERPARTIES)
    amount = Decimal(str(round(random.uniform(1000, 500000), 2)))
    direction = random.choice(["inflow", "outflow"])
    txn_date = base_date + timedelta(days=random.randint(0, 60))
    
    return {
        "id": txn_id,
        "counterparty": counterparty,
        "amount": amount,
        "direction": direction,
        "date": txn_date,
        "currency": "INR",
    }

def apply_discrepancy(base: Dict, disc_type: str, variant: int = 0) -> Dict:
    result = base.copy()
    
    if disc_type == "clean_match":
        pass
    elif disc_type == "amount_mismatch_fee":
        fee = Decimal(str(round(random.uniform(10, 500), 2)))
        if base["direction"] == "inflow":
            result["bank_amount"] = base["amount"] - fee
            result["processor_fee"] = fee
        else:
            result["bank_amount"] = base["amount"] + fee
            result["processor_fee"] = fee
    elif disc_type == "amount_mismatch_rounding":
        diff = Decimal("0.01") if variant % 2 == 0 else Decimal("-0.01")
        result["bank_amount"] = base["amount"] + diff
    elif disc_type == "date_mismatch":
        days = random.randint(1, 3)
        result["bank_date"] = base["date"] + timedelta(days=days)
        result["ledger_date"] = base["date"]
    elif disc_type == "missing_ledger":
        result["missing_source"] = "ledger"
    elif disc_type == "missing_bank":
        result["missing_source"] = "bank"
    elif disc_type == "duplicate_ledger":
        result["duplicate"] = True
    elif disc_type == "reference_error":
        result["ref_typo"] = True
    elif disc_type == "currency_issue":
        result["currency"] = "USD"
        result["fx_rate"] = Decimal("83.0")
    elif disc_type == "ambiguous":
        result["counterparty"] = "UNKNOWN MERCHANT"
        result["description"] = "GENERIC PAYMENT"
    elif disc_type == "processor_fee":
        fee = Decimal(str(round(base["amount"] * Decimal("0.029") + Decimal("30"), 2)))
        result["processor_fee"] = fee
        result["processor_gross"] = base["amount"]
        result["processor_net"] = base["amount"] - fee
        result["bank_amount"] = base["amount"] - fee
    
    return result

def generate_dataset(count: int = 120) -> List[Dict]:
    base_date = date(2026, 7, 1)
    distribution = {
        "clean_match": 70,
        "amount_mismatch_fee": 6,
        "amount_mismatch_rounding": 6,
        "date_mismatch": 8,
        "missing_ledger": 6,
        "missing_bank": 5,
        "duplicate_ledger": 6,
        "reference_error": 4,
        "currency_issue": 2,
        "ambiguous": 4,
        "processor_fee": 5,
    }
    
    txn_id = 1
    records = []
    
    for disc_type, n in distribution.items():
        for i in range(n):
            base = generate_base_transaction(txn_id, base_date)
            modified = apply_discrepancy(base, disc_type, i)
            modified["ground_truth"] = disc_type
            modified["txn_id"] = txn_id
            records.append(modified)
            txn_id += 1
    
    random.shuffle(records)
    for i, r in enumerate(records):
        r["txn_id"] = i + 1
    
    return records

def write_bank_csv(records: List[Dict], filename: str):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "transaction_date", "amount", "currency", "counterparty", "description", "bank_reference", "direction", "dr_cr"])
        for r in records:
            if r.get("missing_source") == "bank":
                continue
            amt = r.get("bank_amount", r["amount"])
            txn_date = r.get("bank_date", r["date"])
            ref = f"BNK{r['txn_id']:06d}"
            if r.get("ref_typo"):
                ref = ref[:-1] + str(random.randint(0,9))
            desc = random.choice(BANK_DESCRIPTIONS)
            dr_cr = "CR" if r["direction"] == "inflow" else "DR"
            writer.writerow([r["txn_id"], txn_date, amt, "INR", r["counterparty"], desc, ref, r["direction"], dr_cr])

def write_ledger_csv(records: List[Dict], filename: str):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "invoice_id", "transaction_date", "amount", "currency", "counterparty", "description", "account", "direction", "status"])
        for r in records:
            if r.get("missing_source") == "ledger":
                continue
            count = 2 if r.get("duplicate") else 1
            for dup in range(count):
                amt = r["amount"]
                txn_date = r.get("ledger_date", r["date"])
                inv_id = f"INV{r['txn_id']:06d}"
                if dup == 1:
                    inv_id += "A"
                desc = random.choice(LEDGER_DESCRIPTIONS)
                account = random.choice(["RECEIVABLES", "PAYABLES", "REVENUE", "EXPENSES"])
                status = "POSTED"
                writer.writerow([r["txn_id"], inv_id, txn_date, amt, "INR", r["counterparty"], desc, account, r["direction"], status])

def write_processor_csv(records: List[Dict], filename: str):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "processor_reference", "transaction_date", "gross_amount", "fee", "net_amount", "currency", "counterparty", "description", "settlement_date"])
        for r in records:
            proc_ref = f"PROC{r['txn_id']:06d}"
            gross = r.get("processor_gross", r["amount"])
            fee = r.get("processor_fee", Decimal("0"))
            net = r.get("processor_net", gross - fee)
            settlement = r["date"] + timedelta(days=random.randint(1, 2))
            if r.get("bank_amount") is not None:
                net = r["bank_amount"]
                fee = gross - net
            desc = random.choice(PROCESSOR_DESCRIPTIONS)
            writer.writerow([r["txn_id"], proc_ref, r["date"], gross, fee, net, "INR", r["counterparty"], desc, settlement])

def write_ground_truth(records: List[Dict], filename: str):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "source", "source_id", "ground_truth_type", "expected_amount", "bank_amount", "ledger_amount", "processor_gross", "processor_fee", "processor_net", "notes"])
        for r in records:
            writer.writerow([
                r["txn_id"], "multi", f"TXN{r['txn_id']:06d}",
                r["ground_truth"], r["amount"],
                r.get("bank_amount", r["amount"]),
                r["amount"],
                r.get("processor_gross", r["amount"]),
                r.get("processor_fee", Decimal("0")),
                r.get("processor_net", r["amount"]),
                f"Variant of {r['ground_truth']}"
            ])

if __name__ == "__main__":
    records = generate_dataset(120)
    
    write_bank_csv(records, "data/bank.csv")
    write_ledger_csv(records, "data/ledger.csv")
    write_processor_csv(records, "data/processor.csv")
    write_ground_truth(records, "data/ground_truth.csv")
    
    import polars as pl
    df = pl.DataFrame(records)
    df.write_parquet("data/ground_truth.parquet")
    
    print(f"Generated {len(records)} records")
    print("Files: data/bank.csv, data/ledger.csv, data/processor.csv, data/ground_truth.csv, data/ground_truth.parquet")
    
    from collections import Counter
    print("\nDistribution:")
    for k, v in Counter(r["ground_truth"] for r in records).items():
        print(f"  {k}: {v}")