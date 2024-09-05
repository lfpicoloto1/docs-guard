terraform {
  required_providers {
    mgc = {
      source = "magalucloud/mgc"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.5.1"
    }
  }
}


resource "mgc_kubernetes_cluster" "cluster" {
  provider = mgc.sudeste
  name                 = "DocsProjects"
  version              = "v1.30.2"
  description          = "InternalProjects"
}

resource "mgc_kubernetes_nodepool" "nodepool" {
  provider = mgc.sudeste
  name         = "DocsGuard"
  cluster_id   = mgc_kubernetes_cluster.cluster.id  # Aqui corrige para cluster.id
  flavor_name  = "cloud-k8s.gp1.small"
  replicas     = 1
  min_replicas = 1
  max_replicas = 5
}

data "mgc_kubernetes_cluster_kubeconfig" "cluster" {
  provider = mgc.sudeste
  cluster_id = mgc_kubernetes_cluster.cluster.id  # Obtém o kubeconfig do cluster criado
}

resource "local_file" "kubeconfig" {
  provider = local
  content  = data.mgc_kubernetes_cluster_kubeconfig.cluster.kubeconfig
  filename = "${path.module}/kubeconfig.yaml"
}
