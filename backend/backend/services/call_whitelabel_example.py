from pprint import pprint

import whitelabel_client
from backend.config import get_settings
from whitelabel_client.rest import ApiException

# See configuration.py for a list of all supported configuration parameters.
configuration = whitelabel_client.Configuration(host=get_settings().whitelabel_endpoint)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: authentication_token
configuration.api_key["authentication_token"] = get_settings().whitelabel_client_key

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['authentication_token'] = 'Bearer'


# Enter a context with an instance of the API client
with whitelabel_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = whitelabel_client.OMSApi(api_client)

    try:
        # lists events
        api_response = api_instance.api_v1_oms_oms_id_get("1")
        print("The response of OMSApi->api_v1_oms_oms_id_get:\n")
        pprint(api_response)
    except ApiException as e:
        print(f"Exception when calling OMSApi->api_v1_oms_oms_id_get: {e}")
