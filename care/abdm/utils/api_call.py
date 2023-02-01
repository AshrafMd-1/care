import json
from base64 import b64encode

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from django.conf import settings
from django.core.cache import cache

GATEWAY_API_URL = "https://dev.abdm.gov.in/"
HEALTH_SERVICE_API_URL = "https://healthidsbx.abdm.gov.in/api"
ABDM_TOKEN_URL = GATEWAY_API_URL + "gateway/v0.5/sessions"
ABDM_GATEWAY_URL = GATEWAY_API_URL + "gateway"
ABDM_TOKEN_CACHE_KEY = "abdm_token"

# TODO: Exception handling for all api calls, need to gracefully handle known exceptions


def encrypt_with_public_key(a_message):
    rsa_public_key = RSA.importKey(
        requests.get(
            HEALTH_SERVICE_API_URL + "/v2/auth/cert", verify=False
        ).text.strip()
    )
    rsa_public_key = PKCS1_v1_5.new(rsa_public_key)
    encrypted_text = rsa_public_key.encrypt(a_message.encode())
    return b64encode(encrypted_text).decode()


class APIGateway:
    def __init__(self, gateway, token):
        if gateway == "health":
            self.url = HEALTH_SERVICE_API_URL
        elif gateway == "abdm":
            self.url = GATEWAY_API_URL
        elif gateway == "abdm_gateway":
            self.url = ABDM_GATEWAY_URL
        else:
            self.url = GATEWAY_API_URL
        self.token = token

    # def encrypt(self, data):
    #     cert = cache.get("abdm_cert")
    #     if not cert:
    #         cert = requests.get(settings.ABDM_CERT_URL).text
    #         cache.set("abdm_cert", cert, 3600)

    def add_user_header(self, headers, user_token):
        headers.update(
            {
                "X-Token": "Bearer " + user_token,
            }
        )
        return headers

    def add_auth_header(self, headers):
        token = cache.get(ABDM_TOKEN_CACHE_KEY)
        print("Using Cached Token")
        if not token:
            print("No Token in Cache")
            data = {
                "clientId": settings.ABDM_CLIENT_ID,
                "clientSecret": settings.ABDM_CLIENT_SECRET,
            }
            auth_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            resp = requests.post(
                ABDM_TOKEN_URL,
                data=json.dumps(data),
                headers=auth_headers,
                verify=False,
            )
            print("Token Response Status: {}".format(resp.status_code))
            if resp.status_code < 300:
                # Checking if Content-Type is application/json
                if resp.headers["Content-Type"] != "application/json":
                    print(
                        "Unsupported Content-Type: {}".format(
                            resp.headers["Content-Type"]
                        )
                    )
                    print("Response: {}".format(resp.text))
                    return None
                else:
                    data = resp.json()
                    token = data["accessToken"]
                    expires_in = data["expiresIn"]
                    print("New Token: {}".format(token))
                    print("Expires in: {}".format(expires_in))
                    cache.set(ABDM_TOKEN_CACHE_KEY, token, expires_in)
            else:
                print("Bad Response: {}".format(resp.text))
                return None
        # print("Returning Authorization Header: Bearer {}".format(token))
        print("Adding Authorization Header")
        auth_header = {"Authorization": "Bearer {}".format(token)}
        return {**headers, **auth_header}

    def add_additional_headers(self, headers, additional_headers):
        return {**headers, **additional_headers}

    def get(self, path, params=None, auth=None):
        url = self.url + path
        headers = {}
        headers = self.add_auth_header(headers)
        if auth:
            headers = self.add_user_header(headers, auth)
        print("Making GET Request to: {}".format(url))
        response = requests.get(url, headers=headers, params=params, verify=False)
        print("{} Response: {}".format(response.status_code, response.text))
        return response

    def post(self, path, data=None, auth=None, additional_headers=None):
        url = self.url + path
        headers = {
            "Content-Type": "application/json",
            "accept": "*/*",
            "Accept-Language": "en-US",
        }
        headers = self.add_auth_header(headers)
        if auth:
            headers = self.add_user_header(headers, auth)
        if additional_headers:
            headers = self.add_additional_headers(headers, additional_headers)
        # headers_string = " ".join(
        #     ['-H "{}: {}"'.format(k, v) for k, v in headers.items()]
        # )
        data_json = json.dumps(data)
        # print("curl -X POST {} {} -d {}".format(url, headers_string, data_json))
        print("Posting Request to: {}".format(url))
        response = requests.post(url, headers=headers, data=data_json, verify=False)
        print("{} Response: {}".format(response.status_code, response.text))
        return response


class HealthIdGateway:
    def __init__(self):
        self.api = APIGateway("health", None)

    def generate_aadhaar_otp(self, data):
        path = "/v1/registration/aadhaar/generateOtp"
        response = self.api.post(path, data)
        print("{} Response: {}".format(response.status_code, response.text))
        return response.json()

    def resend_aadhaar_otp(self, data):
        path = "/v1/registration/aadhaar/resendAadhaarOtp"
        response = self.api.post(path, data)
        return response.json()

    def verify_aadhaar_otp(self, data):
        path = "/v1/registration/aadhaar/verifyOTP"
        response = self.api.post(path, data)
        return response.json()

    def generate_mobile_otp(self, data):
        path = "/v1/registration/aadhaar/generateMobileOTP"
        response = self.api.post(path, data)
        return response.json()

    # /v1/registration/aadhaar/verifyMobileOTP
    def verify_mobile_otp(self, data):
        path = "/v1/registration/aadhaar/verifyMobileOTP"
        response = self.api.post(path, data)
        return response.json()

    # /v1/registration/aadhaar/createHealthIdWithPreVerified
    def create_health_id(self, data):
        path = "/v1/registration/aadhaar/createHealthIdWithPreVerified"
        print("Creating Health ID with data: {}".format(data))
        data.pop("healthId", None)
        response = self.api.post(path, data)
        return response.json()

    # /v1/search/existsByHealthId
    # API checks if ABHA Address/ABHA Number is reserved/used which includes permanently deleted ABHA Addresses
    # Return { status: true }
    def exists_by_health_id(self, data):
        path = "/v1/search/existsByHealthId"
        response = self.api.post(path, data)
        return response.json()

    # /v1/search/searchByHealthId
    # API returns only Active or Deactive ABHA Number/ Address (Never returns Permanently Deleted ABHA Number/Address)
    # Returns {
    # "authMethods": [
    #     "AADHAAR_OTP"
    # ],
    # "healthId": "deepakndhm",
    # "healthIdNumber": "43-4221-5105-6749",
    # "name": "kishan kumar singh",
    # "status": "ACTIVE"
    # }
    def search_by_health_id(self, data):
        path = "/v1/search/searchByHealthId"
        response = self.api.post(path, data)
        return response.json()

    # /v1/search/searchByMobile
    def search_by_mobile(self, data):
        path = "/v1/search/searchByMobile"
        response = self.api.post(path, data)
        return response.json()

    # Auth APIs

    # /v1/auth/init
    def auth_init(self, data):
        path = "/v1/auth/init"
        response = self.api.post(path, data)
        return response.json()

    # /v1/auth/confirmWithAadhaarOtp
    def confirm_with_aadhaar_otp(self, data):
        path = "/v1/auth/confirmWithAadhaarOtp"
        response = self.api.post(path, data)
        return response.json()

    # /v1/auth/confirmWithMobileOTP
    def confirm_with_mobile_otp(self, data):
        path = "/v1/auth/confirmWithMobileOTP"
        response = self.api.post(path, data)
        return response.json()

    # /v1/auth/confirmWithDemographics
    def confirm_with_demographics(self, data):
        path = "/v1/auth/confirmWithDemographics"
        response = self.api.post(path, data)
        return response.json()

    # /v1/auth/generate/access-token
    def generate_access_token(self, data):
        if "access_token" in data:
            return data["access_token"]
        elif "accessToken" in data:
            return data["accessToken"]
        elif "token" in data:
            return data["token"]

        if "refreshToken" in data:
            refreshToken = data["refreshToken"]
        elif "refresh_token" in data:
            refreshToken = data["refresh_token"]
        else:
            return None
        path = "/v1/auth/generate/access-token"
        response = self.api.post(path, {"refreshToken": refreshToken})
        return response.json()["accessToken"]

    # Account APIs

    # /v1/account/profile
    def get_profile(self, data):
        path = "/v1/account/profile"
        access_token = self.generate_access_token(data)
        response = self.api.get(path, {}, access_token)
        return response.json()

    # /v1/account/qrCode
    def get_qr_code(self, data, auth):
        path = "/v1/account/qrCode"
        access_token = self.generate_access_token(data)
        print("Getting QR Code for: {}".format(data))
        response = self.api.get(path, {}, access_token)
        print("QR Code Response: {}".format(response.text))
        return response.json()


class HealthIdGatewayV2:
    def __init__(self):
        self.api = APIGateway("health", None)

    # V2 APIs
    def generate_aadhaar_otp(self, data):
        path = "/v2/registration/aadhaar/generateOtp"
        data["aadhaar"] = encrypt_with_public_key(data["aadhaar"])
        data.pop("cancelToken", {})
        response = self.api.post(path, data)
        return response.json()

    def generate_document_mobile_otp(self, data):
        path = "/v2/document/generate/mobile/otp"
        data["mobile"] = "ENTER MOBILE NUMBER HERE"  # Hard Coding for test
        data.pop("cancelToken", {})
        response = self.api.post(path, data)
        return response.json()

    def verify_document_mobile_otp(self, data):
        path = "/v2/document/verify/mobile/otp"
        data["otp"] = encrypt_with_public_key(data["otp"])
        data.pop("cancelToken", {})
        response = self.api.post(path, data)
        return response.json()


class AbdmGateway:
    def __init__(self):
        self.api = APIGateway("abdm_gateway", None)

    # /v0.5/users/auth/fetch-modes
    def fetch_modes(self, data):
        path = "/v0.5/users/auth/fetch-modes"
        response = self.api.post(path, data)
        return response.json()

    # /v1.0/patients/profile/on-share
    def on_share(self, data):
        path = "/v1.0/patients/profile/on-share"
        additional_headers = {"X-CM-ID": "sbx"}
        response = self.api.post(path, data, None, additional_headers)
        return response
