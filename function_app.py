import azure.functions as func
from services import predict_service
import logging
import json
import re

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

GUID_REGEX = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
N_PAST_MONTHS = 6

@app.route(route="predict-health-measures", methods=["POST"])
def prediction_model(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = req.get_json()
        device_record_id = body.get("petTrackerDeviceRecordId")

        if not re.match(GUID_REGEX, device_record_id):
            return func.HttpResponse(
                "Invalid GUID",
                status_code=400
            )
        
        # TODO: CALL SERVICE
        result = predict_service.make_future_health_measures(N_PAST_MONTHS, device_record_id)
        result_str = json.dumps(result)

        return func.HttpResponse(
            result_str,
            status_code=200
        )
    
    except Exception as e:
        return func.HttpResponse(
            f"Unexpected Error: {str(e)}",
            status_code=500
        )