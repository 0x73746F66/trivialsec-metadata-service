locals {
    python_version      = "python3.9"
    aws_default_region  = "ap-southeast-2"
    source_file         = "lambda-metadata-service.zip"
    asset_bucket        = "assets-trivialsec"
    builder_dir         = "sqlite-lambda-layer"
    sqlite_version      = "3370100"
}
