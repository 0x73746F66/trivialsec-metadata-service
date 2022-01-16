resource "aws_iam_role" "metadata_service_role" {
  name               = "metadata_service_role"
  assume_role_policy = templatefile("${path.module}/policy/metadata_service_policy.json", {
    asset_bucket = local.asset_bucket
  })
  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_iam_policy" "metadata_service_policy" {
  name        = "metadata_service_policy"
  path        = "/"
  policy      = file("${path.module}/policy/metadata_service_role_policy.json")
}
resource "aws_iam_role_policy_attachment" "policy_attach" {
  role       = aws_iam_role.metadata_service_role.name
  policy_arn = aws_iam_policy.metadata_service_policy.arn
}

output "metadata_service_role" {
  value = aws_iam_role.metadata_service_role.name
}

output "metadata_service_role_arn" {
  value = aws_iam_role.metadata_service_role.arn
}

output "metadata_service_policy_arn" {
  value = aws_iam_policy.metadata_service_policy.arn
}