import os
from concurrent.futures import ThreadPoolExecutor

from kubernetes import client, config


def delete_ips_in_nonexistent_namespaces():
    """Deletes all kube-ovn CR IPs when spec.namespace value is a namespace not existing."""

    os.environ["AWS_PROFILE"] = "TBD"
    config.load_kube_config(context="TBD")

    custom_api = client.CustomObjectsApi()
    core_api = client.CoreV1Api()

    crd_group = "kubeovn.io"
    crd_version = "v1"
    crd_plural = "ips"

    try:
        ips = custom_api.list_cluster_custom_object(crd_group, crd_version, crd_plural)
    except client.ApiException as e:
        print(f"Error listing IPs: {e}")
        return

    with ThreadPoolExecutor() as executor:
        # Submit each IP to the thread pool for processing
        futures = [
            executor.submit(
                process_ip, ip, core_api, custom_api, crd_group, crd_version, crd_plural
            )
            for ip in ips["items"]
        ]

        # Wait for all futures to complete
        for future in futures:
            future.result()


def process_ip(ip, core_api, custom_api, crd_group, crd_version, crd_plural):
    """Processes a single IP to check if the namespace exists and deletes it if not."""
    namespace = ip["spec"].get("namespace")
    ip_name = ip["metadata"]["name"]
    if not namespace:
        return

    try:
        core_api.read_namespace(namespace)
    except client.ApiException as e:
        if e.status == 404:  # Namespace not found
            try:
                remove_finalizer(
                    custom_api, crd_group, crd_version, namespace, crd_plural, ip_name
                )
                custom_api.delete_cluster_custom_object(
                    crd_group, crd_version, crd_plural, ip["metadata"]["name"]
                )
                print(f"Deleted IP {ip_name} in non-existent namespace {namespace}")
            except client.ApiException as e:
                print(f"Error deleting IP {ip_name}: {e}")
        else:
            print(f"Error checking namespace {namespace}: {e}")


def remove_finalizer(custom_api, crd_group, crd_version, namespace, crd_plural, name):
    """Removes the finalizer from the cluster custom object using a patch."""
    try:
        patch_body = {"metadata": {"finalizers": []}}
        custom_api.patch_cluster_custom_object(
            crd_group, crd_version, crd_plural, name, patch_body
        )
        print(f"Successfully removed finalizer for {name} in namespace {namespace}")
    except client.ApiException as e:
        print(f"Error removing finalizer for {name} in namespace {namespace}: {e}")


if __name__ == "__main__":
    delete_ips_in_nonexistent_namespaces()
