import argparse
import boto3
import json
import datetime
from kubernetes import client, config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def get_ondemand_instance_price(instance_type, pricing_client):
    response = pricing_client.get_products(
        ServiceCode="AmazonEC2",
        Filters=[
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
        ],
    )

    for price_item in response["PriceList"]:
        price_item = json.loads(price_item)
        for term in price_item["terms"]["OnDemand"].values():
            for price_dimension in term["priceDimensions"].values():
                return float(price_dimension["pricePerUnit"]["USD"])

    return 0.0


def get_spot_instance_price(instance_type, ec2_client):
    try:
        response = ec2_client.describe_spot_price_history(
            InstanceTypes=[instance_type],
            ProductDescriptions=["Linux/UNIX"],
            StartTime=datetime.datetime.now(datetime.UTC),
            MaxResults=1,
        )

        if "SpotPriceHistory" in response and len(response["SpotPriceHistory"]) > 0:
            spot_price = response["SpotPriceHistory"][0]
            return float(spot_price["SpotPrice"])
        else:
            return 0.0

    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credential error: {str(e)}")
        return 0.0
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 0.0


def get_instance_price(instance_type, capacity_type, pricing_client, ec2_client):
    # If the capacity type label is undefined, the node is not managed by Karpenter but an on-demand critical node.
    if capacity_type and capacity_type.lower() == "spot":
        price = get_spot_instance_price(instance_type, ec2_client)
    else:
        price = get_ondemand_instance_price(instance_type, pricing_client)

    if price == 0.0:
        print(
            f"Price not found for instance type: {instance_type} with capacity {capacity_type}"
        )
    return price


def calculate_total_cost(instance_dict, pricing_client, ec2_client):
    total_cost = 0.0

    for instance_info in instance_dict:
        instance_type = instance_info["instance_type"]
        capacity_type = instance_info["capacity_type"]

        price = get_instance_price(
            instance_type, capacity_type, pricing_client, ec2_client
        )
        total_cost += price * instance_info["count"]

    return total_cost


def get_instance_counts_from_k8s():
    v1 = client.CoreV1Api()
    nodes = v1.list_node()
    print(f"Total number of nodes: {len(nodes.items)}")

    instance_counts = []
    for node in nodes.items:
        instance_type = node.metadata.labels.get("beta.kubernetes.io/instance-type")
        capacity_type = node.metadata.labels.get("karpenter.sh/capacity-type")

        if instance_type:
            instance_info = next(
                (
                    item
                    for item in instance_counts
                    if item["instance_type"] == instance_type
                    and item["capacity_type"] == capacity_type
                ),
                None,
            )
            if instance_info:
                instance_info["count"] += 1
            else:
                instance_counts.append(
                    {
                        "instance_type": instance_type,
                        "capacity_type": capacity_type,
                        "count": 1,
                    }
                )

    return instance_counts


def main():
    parser = argparse.ArgumentParser(
        description="Calculate total cost of Kubernetes instances."
    )
    parser.add_argument("--k8s-context", help="Specify the Kubernetes context to use")
    parser.add_argument(
        "--aws-profile", help="Specify the AWS profile name to use", default="default"
    )
    args = parser.parse_args()

    print(f"Using Kubernetes context: {args.k8s_context}")
    config.load_kube_config(context=args.k8s_context)

    print(f"Using AWS profile: {args.aws_profile}")
    session = boto3.Session(profile_name=args.aws_profile)
    pricing_client = session.client("pricing", region_name="us-east-1")
    ec2_client = session.client("ec2", region_name="us-east-1")

    instances = get_instance_counts_from_k8s()
    formatted_instances = json.dumps(instances, indent=4)
    print(f"Instances: {formatted_instances}")

    total_cost = calculate_total_cost(instances, pricing_client, ec2_client)
    print(f"Total cost per hour: ${total_cost:.2f}")


if __name__ == "__main__":
    main()
