#!/usr/bin/env bash
# Installs cluster add-ons: Prometheus + Grafana, and the AWS Load Balancer Controller.
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-visitor-tracker-eks}"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.adminPassword="${GRAFANA_PASSWORD:?set GRAFANA_PASSWORD}"

# The controller's IAM permissions come from an EKS Pod Identity association for the
# kube-system/aws-load-balancer-controller service account (see docs/console-deploy-guide.md).
AWS_REGION="${AWS_REGION:-us-east-1}"
VPC_ID=$(aws eks describe-cluster --name "$CLUSTER_NAME" --region "$AWS_REGION" \
  --query cluster.resourcesVpcConfig.vpcId --output text)
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace kube-system --set clusterName="$CLUSTER_NAME" \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region="$AWS_REGION" --set vpcId="$VPC_ID"

kubectl create namespace visitor-tracker --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f "$(dirname "$0")/alerts.yaml"
