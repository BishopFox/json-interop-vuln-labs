from flask import Flask, request
import jsonschema
import requests
import json

app = Flask(__name__)

productDB = None
with open("productDB.json", "r") as fd:
    productDB = json.loads(fd.read())

schema = {
    "type": "object",
    "properties": {
        "orderId": {
            "type": "number",
            "maximum": 10,
        },
        "cart": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "number",
                        "minimum": 0,
                        "exclusiveMaximum": 9 #len(productDB)-1
                    },
                    "qty": {
                        "type": "integer",
                        "minimum": 1
                    },
                },
                "required": ["id", "qty"],
            }
        }
    },
    "required": ["orderId", "cart"],
}


@app.route('/cart/checkout', methods=["POST"])
def checkout():
    # 1a: Parse JSON body using Python stdlib parser.
    data = request.get_json(force=True)

    # 1b: Validate constraints using jsonschema: id: 0 <= x <= 10 and qty: >= 1
    jsonschema.validate(instance=data, schema=schema)

    # 2: Process payments
    resp = requests.request(method="POST",
                            url="http://payments:8000/process",
                            data=request.get_data(),
                            )

    # 3: Print receipt as a response, or produce generic error message
    if resp.status_code == 200:
        receipt = "Receipt:\n"
        for item in data["cart"]:
            receipt += "{}x {} @ ${}/unit\n".format(
                item["qty"],
                productDB[item["id"]].get("name"),
                productDB[item["id"]].get("price")
            )
        receipt += "\nTotal Charged: ${}\n".format(resp.json()["total"])
        return receipt
    return "Error during payment processing"
