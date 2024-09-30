import requests
import time
import json
import os

from requests.auth import HTTPBasicAuth


class Subscription:
    def __init__(self, topic):
        self.topic = topic


class Queue:
    def __init__(self, name, msg_vpn_name, access_type, maxMsgSpoolUsage, permission, ingress_enabled, egress_enabled,
                 subscribed_topics):
        self.name = name
        self.msg_vpn_name = msg_vpn_name
        self.access_type = access_type
        self.maxMsgSpoolUsage = maxMsgSpoolUsage
        self.permission = permission
        self.ingress_enabled = ingress_enabled
        self.egress_enabled = egress_enabled
        self.subscribed_topics = subscribed_topics


def populate_queues(queues):

    for queue in queues:

        print("Sending request to create queue: " + queue.name)

        print("\n -------- \n")

        queue_req_payload = {
            'queueName': queue.name,
            'permission': queue.permission,
            'accessType': queue.access_type,
            'maxMsgSpoolUsage': queue.maxMsgSpoolUsage,
            'ingressEnabled': queue.ingress_enabled,
            'egressEnabled': queue.egress_enabled
        }
        req_url = "http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + queue.msg_vpn_name + "/queues"

        queue_req = requests.post(url=req_url, json=queue_req_payload, headers=content_header, auth=basic)

        print(queue_req.text)

        queue_check = requests.get(
            url="http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + queue.msg_vpn_name + "/queues/"
                + queue.name, auth=basic)

        while queue_check.status_code != 200:
            print(queue_check.status_code)

            queue_check = requests.get(
                url="http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + queue.msg_vpn_name + "/queues/"
                    + queue.name, auth=basic)

        print("\n -------- \n")
        print("Queue creation successful! : " + queue.name)

        for subscribed_topic in queue.subscribed_topics:
            print(
                "Sending request to create subscribed topic: " + subscribed_topic.topic +
                " --- for queue: " + queue.name)

            topic_req_payload = {
                'subscriptionTopic': subscribed_topic.topic
            }

            req_url = ("http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + queue.msg_vpn_name + "/queues/"
                       + queue.name + "/subscriptions")

            topic_req = requests.post(url=req_url,
                                      json=topic_req_payload,
                                      headers=content_header,
                                      auth=basic)

            print(topic_req.text)


def patch_msg_vpn(msg_vpn_name, basic_auth):

    req_payload = {
        'authenticationBasicType': 'internal'
    }

    req_url = "http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + msg_vpn_name
    response = requests.patch(url=req_url, json=req_payload, headers=content_header, auth=basic_auth)
    print("patch_msg_vpn() yields: " + str(response.status_code))


def patch_client_username(msg_vpn_name, client_username_in, new_password, basic_auth):

    req_payload = {
        'password': new_password
    }

    req_url = "http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + msg_vpn_name + "/clientUsernames/" + client_username_in
    response = requests.patch(url=req_url, json=req_payload, headers=content_header, auth=basic_auth)
    print("patch_client_username() yields: " + str(response.status_code))


def patch_client_profile_config(msg_vpn_name, client_profile_to_patch, body, basic_auth):

    req_payload = body

    req_url = "http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + msg_vpn_name + "/clientProfiles/" + client_profile_to_patch
    response = requests.patch(url=req_url, json=req_payload, headers=content_header, auth=basic_auth)
    print("patch_client_profile_config() yields: " + str(response.status_code))


def create_telemetry_profile(msg_vpn_name, profile_name, filter_name, basic_auth):

    profile_payload = {
        'msgVpnName': msg_vpn_name,
        'receiverAclConnectDefaultAction': "allow",
        'receiverEnabled': True,
        'telemetryProfileName': profile_name,
        'traceEnabled': True
    }

    profile_url = "http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + msg_vpn_name + "/telemetryProfiles"

    profile_response = requests.post(url=profile_url, json=profile_payload, headers=content_header, auth=basic_auth)
    print("Telemetry profile creation: " + str(profile_response.status_code))

    filters_url = profile_url + "/" + profile_name + "/traceFilters"

    filters_payload = {
      'enabled': True,
      'msgVpnName': msg_vpn_name,
      'telemetryProfileName': profile_name,
      'traceFilterName': filter_name
    }

    filter_response = requests.post(url=filters_url, json=filters_payload, headers=content_header, auth=basic_auth)
    print("Telemetry profile filter creation: " + str(filter_response.status_code))

    sub_filter_url = filters_url + "/" + filter_name + "/subscriptions"

    sub_filter_payload = {
        'msgVpnName': msg_vpn_name,
        'subscription': ">",
        'subscriptionSyntax': "smf",
        'telemetryProfileName': profile_name,
        'traceFilterName': filter_name
    }

    sub_filter_response = requests.post(url=sub_filter_url, json=sub_filter_payload, headers=content_header, auth=basic_auth)
    print("filter subscription creation: " + str(sub_filter_response.status_code))


def configure_collector_client_username(msg_vpn_name, body, basic_auth):
    req_url = "http://" + host_name + ":" + port + "/SEMP/v2/config/msgVpns/" + msg_vpn_name + "/clientUsernames"
    payload = body

    profile_response = requests.post(url=req_url, json=payload, headers=content_header, auth=basic_auth)
    print("configure_collector_client_username() yields: " + str(profile_response.status_code))


r = requests.Response()
r.status_code = 400

dir_path = os.path.dirname(os.path.realpath(__file__))
json_file_path = dir_path + os.sep + "dt-setup.json"

host_name = "solace"
port = "8080"

username = "admin"
password = "admin"

msg_vpn = "default"
client_profile = "default"

client_username = {}
telemetry_profile = {}

collector_client_username = {}

json_queues = []

content_header = {'Content-Type': 'application/json', 'Accept': 'application/json'}

print(dir_path)
try:
    with open(json_file_path, mode="r", encoding="utf-8") as read_file:
        print("file opening successful")
        json_data = json.load(read_file)
        print("json data assign successful")

    json_vars = [
        host_name,
        port,
        username,
        password,
        msg_vpn,
        client_profile,
        client_username,
        telemetry_profile,
        collector_client_username
    ]

    keys = [
        "hostname",
        "port",
        "username",
        "password",
        "msg_vpn_name",
        "client_profile",
        "client_username",
        "telemetry_profile",
        "collector_client_username"
    ]

    print("assigning...")

    for i in range(len(keys)):
        # print(keys[i])
        try:
            json_vars[i] = json_data[keys[i]]
        except KeyError:
            print("the field " + keys[i] + " is not present in the json file")

    host_name = json_vars[0]
    port = json_vars[1]

    print("host acquired")
    print(host_name)
    print(port)

    username = json_vars[2]
    password = json_vars[3]

    msg_vpn = json_vars[4]
    client_profile = json_vars[5]

    client_username = json_vars[6]
    telemetry_profile = json_vars[7]
    collector_client_username = json_vars[8]

    for json_queue in json_data["queues"]:
        print(json_queue["name"])
        subscriptions = []
        for sub in json_queue["subscribed_topics"]:
            subscriptions.append(Subscription(sub["name"]))
        json_queues.append(
            Queue(
                name=json_queue["name"],
                msg_vpn_name=json_queue["msg_vpn_name"],
                access_type=json_queue["access_type"],
                maxMsgSpoolUsage=json_queue["maxMsgSpoolUsage"],
                permission=json_queue["permission"],
                ingress_enabled=json_queue["ingress_enabled"],
                egress_enabled=json_queue["egress_enabled"],
                subscribed_topics=subscriptions
            )
        )

except FileNotFoundError:
    print("error encountered parsing json file")

basic = HTTPBasicAuth(username, password)

while r.status_code != 200:

    print("Attempting connection to Solace Event Broker...")
    try:
        r = requests.get(url="http://" + host_name + ":" + port + "/")
    except RuntimeError:
        print("Connection Failed, retrying...")
        time.sleep(1)

print("Connection successful!")

patch_msg_vpn(msg_vpn, basic)

patch_client_username(msg_vpn, client_username["username"], client_username["new_password"], basic)

client_profile_patch_body = {
  'allowGuaranteedMsgReceiveEnabled': True,
  'allowGuaranteedMsgSendEnabled': True,
  'rejectMsgToSenderOnNoSubscriptionMatchEnabled': True
}

patch_client_profile_config(msg_vpn, client_profile, client_profile_patch_body, basic)

create_telemetry_profile(msg_vpn, telemetry_profile["name"], telemetry_profile["filter_name"], basic)

configure_collector_client_username(msg_vpn, collector_client_username, basic)

populate_queues(json_queues)

print("Queues and Topic creation finished")
