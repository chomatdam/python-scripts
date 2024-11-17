# AWS Cost Estimator

## Steps

1. **Specify Instance Types and Capacity**: Pull instance types and capacity types (spot or on-demand) from a
user-provided Kubernetes context.
2. **Fetch Pricing Information**: The script will query the AWS Pricing API to retrieve pricing information.
3. **Calculate Cost**: It calculates the total cost on a per-hour basis.

## How to use
**Command**
```shell
uv run by_instance_type --k8s-context "arn:$partition:eks:$region:$accountId:cluster/$name" --aws-profile "$profileName"
```
**Stdout**
```json
Using Kubernetes context: arn:$partition:eks:$region:$accountId:cluster/$name
Using AWS profile: "$profileName"
Total number of nodes: 27
Instances: [
    {
        "instance_type": "c5n.2xlarge",
        "capacity_type": "spot",
        "count": 2
    },
    {
        "instance_type": "c5a.2xlarge",
        "capacity_type": "on-demand",
        "count": 10
    },
    ...
]
Total cost per hour: $9.76
```

**NOTE**
- The pricing API used is on the `us-east-1` region, you need active AWS credentials on this AWS partition.
