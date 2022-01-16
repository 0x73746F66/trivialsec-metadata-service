resource "aws_lambda_function" "metadata_service" {
  filename      = "${abspath(path.module)}/${local.source_file}"
  source_code_hash = filebase64sha256("${abspath(path.module)}/${local.source_file}")
  function_name = "metadata-service"
  role          = aws_iam_role.metadata_service_role.arn
  handler       = "handler.lambda_handler"
  runtime       = local.python_version
  timeout       = 900

  environment {
    variables = {
      BUILD_ENV = var.build_env
    }
  }
  lifecycle {
    create_before_destroy = true
  }
  depends_on    = [
    aws_iam_role_policy_attachment.policy_attach
  ]
}
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.metadata_service.arn
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${local.asset_bucket}"
}
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = local.asset_bucket
  lambda_function {
    lambda_function_arn = aws_lambda_function.metadata_service.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "metadata-service/"
    filter_suffix       = ".queue"
  }
  depends_on = [aws_lambda_permission.allow_bucket]
}
output "metadata_service_arn" {
    value = aws_lambda_function.metadata_service.arn
}
