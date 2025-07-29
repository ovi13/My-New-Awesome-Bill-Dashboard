from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# Predefined fixed data for users
fixed_data = {
    "Motor Bill": {"consumer_id": "41771313", "meter_number": "10501785"},
    "Mridul Kanti Dey": {"consumer_id": "41793600", "meter_number": "250145"},
    "Rita Dey": {"consumer_id": "41569338", "meter_number": "094222"},
    "Pijush Kanti Dey": {"consumer_id": "41019683", "meter_number": "27023"},
    "Angshu Debray": {"consumer_id": "41569323", "meter_number": "094221"},
    "Gas Bill": {"consumer_id": "240101995", "meter_number": None}
}


# Function to calculate total bill and balance
def calculate_invoice(gas, electricity, motor, bkash_charge, paid):
    total_bill = gas + electricity + motor + bkash_charge
    balance = paid - total_bill
    return total_bill, balance


@app.route('/')
def home():
    """Renders the home page."""
    return render_template('home.html')


@app.route('/bill_form')
def bill_form():
    """Renders the invoice generation form (formerly index.html)."""
    return render_template('bill_form.html', fixed_data=fixed_data)


@app.route('/calculator')
def calculator():
    """Renders the bill calculator page."""
    return render_template('calculator.html', fixed_data=fixed_data)


@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    selected_user = request.form.get('user')
    name = selected_user  # Default name
    consumer_id = ""
    meter_number = ""

    # Initialize all possible bill components to 0.0
    motor_bill = 0.0
    gas_bill = 0.0
    electricity_bill = 0.0
    bkash_charge = 0.0
    total_paid = 0.0

    transaction_types = []
    transaction_ids = []

    billing_month = request.form.get('billing_month')

    # --- Robust Data Extraction based on selected_user ---
    # Retrieve data based on which form section was active
    if selected_user == "Enter Custom Data":
        name = request.form.get('name_custom', 'Custom User')
        consumer_id = request.form.get('consumer_id_custom', '')
        meter_number = request.form.get('meter_number_custom', '')
        electricity_bill = float(request.form.get('electricity_bill_custom') or 0.0)
        motor_bill = float(request.form.get('motor_bill_custom') or 0.0)
        bkash_charge = float(request.form.get('bkash_charge_custom') or 0.0)
        total_paid = float(request.form.get('total_paid_custom') or 0.0)

        transaction_types = request.form.getlist('transaction_types_custom[]')
        transaction_ids = request.form.getlist('transaction_ids_custom[]')

    elif selected_user == "Motor Bill":
        name = "Motor Bill"
        consumer_id = fixed_data["Motor Bill"]["consumer_id"]
        meter_number = fixed_data["Motor Bill"]["meter_number"]
        motor_bill = float(request.form.get('motor_bill_motor') or 0.0)
        bkash_charge = float(request.form.get('bkash_charge_motor') or 0.0)
        total_paid = float(request.form.get('total_paid_motor') or 0.0)

        transaction_types = request.form.getlist('transaction_types_motor[]')
        transaction_ids = request.form.getlist('transaction_ids_motor[]')

    elif selected_user == "Gas Bill":
        name = "Gas Bill"
        consumer_id = fixed_data["Gas Bill"]["consumer_id"]
        meter_number = fixed_data["Gas Bill"]["meter_number"]
        gas_bill = float(request.form.get('gas_bill_gas') or 0.0)  # Should be 6480.0 from readonly field
        bkash_charge = float(request.form.get('bkash_charge_gas') or 0.0)
        total_paid = float(request.form.get('total_paid_gas') or 0.0)

        transaction_types = request.form.getlist('transaction_types_gas[]')
        transaction_ids = request.form.getlist('transaction_ids_gas[]')

    elif selected_user in fixed_data:  # For Mridul, Rita, Pijush, Angshu Debray (Individual Predefined Users)
        # Name and IDs are from fixed_data
        consumer_id = fixed_data[selected_user]["consumer_id"]
        meter_number = fixed_data[selected_user]["meter_number"]

        electricity_bill = float(request.form.get('electricity_bill_individual') or 0.0)
        motor_bill = float(request.form.get('motor_bill_individual') or 0.0)
        gas_bill = float(request.form.get('gas_bill_individual') or 0.0)  # Individual gas bill might be different
        bkash_charge = float(request.form.get('bkash_charge_individual') or 0.0)
        total_paid = float(request.form.get('total_paid_individual') or 0.0)

        transaction_types = request.form.getlist('transaction_types_individual[]')
        transaction_ids = request.form.getlist('transaction_ids_individual[]')

    # Initialize shared bill values (these are specific to how Motor/Gas Bill types are handled)
    motor_bill_mridul = 0.0
    motor_bill_rita = 0.0
    gas_bill_mridul = 0.0
    gas_bill_pappu = 0.0
    gas_bill_rita = 0.0
    gas_bill_pijush = 0.0

    if selected_user == "Motor Bill" and motor_bill > 0:
        motor_bill_mridul = motor_bill / 2
        motor_bill_rita = motor_bill / 2

    if selected_user == "Gas Bill":
        gas_bill = 6480.0  # This is a fixed value for the "Gas Bill" option
        gas_bill_mridul = 2160.0
        gas_bill_pappu = 2160.0
        gas_bill_rita = 1080.0
        gas_bill_pijush = 1080.0

    # Combine transaction types and IDs into a list of dictionaries
    combined_transactions = []
    min_len = min(len(transaction_types), len(transaction_ids))
    for i in range(min_len):
        if transaction_types[i] and transaction_ids[i]:
            combined_transactions.append({
                "type": transaction_types[i],
                "id": transaction_ids[i]
            })

    total_bill, balance = calculate_invoice(gas_bill, electricity_bill, motor_bill, bkash_charge, total_paid)

    current_datetime = datetime.now()
    billing_date = current_datetime.strftime("%Y-%m-%d")
    billing_time = current_datetime.strftime("%I:%M %p")

    return render_template('invoice.html',
                           name=name,
                           consumer_id=consumer_id,
                           meter_number=meter_number,
                           billing_month=billing_month,
                           gas_bill=gas_bill,
                           electricity_bill=electricity_bill,
                           motor_bill=motor_bill,
                           motor_bill_mridul=motor_bill_mridul,
                           motor_bill_rita=motor_bill_rita,
                           gas_bill_mridul=gas_bill_mridul,
                           gas_bill_pappu=gas_bill_pappu,
                           gas_bill_rita=gas_bill_rita,
                           gas_bill_pijush=gas_bill_pijush,
                           bkash_charge=bkash_charge,
                           total_bill=total_bill,
                           total_paid=total_paid,
                           balance=balance,
                           billing_date=billing_date,
                           billing_time=billing_time,
                           combined_transactions=combined_transactions)


if __name__ == '__main__':
    app.run(debug=True)