# 1. Define the AWS Provider
provider "aws" {
  region = "us-east-1"
}

# 2. Get the current AWS Account ID (needed for policies)
data "aws_caller_identity" "current" {}

# 3. Create the S3 Bucket for our HR documents
resource "aws_s3_bucket" "hr_data_bucket" {
  bucket        = "hr-rag-data-${data.aws_caller_identity.current.account_id}" # Must be globally unique
  force_destroy = true # Allows Terraform to delete the bucket later even if we put files in it
}

# 4. Create the IAM Trust Policy for Bedrock
# This tells AWS: "The Bedrock service is allowed to assume this role."
data "aws_iam_policy_document" "bedrock_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

# 5. Create the IAM Role for the Knowledge Base
resource "aws_iam_role" "knowledge_base_role" {
  name               = "AmazonBedrockExecutionRoleForKB"
  assume_role_policy = data.aws_iam_policy_document.bedrock_trust_policy.json
}

# 6. Create an IAM Policy allowing Bedrock to read the S3 bucket
resource "aws_iam_role_policy" "kb_s3_policy" {
  name = "BedrockKBS3Access"
  role = aws_iam_role.knowledge_base_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.hr_data_bucket.arn,
          "${aws_s3_bucket.hr_data_bucket.arn}/*"
        ]
      }
    ]
  })
}


  # For this project, we are letting AWS manage the vector database backend automatically
  # to save us from writing 100+ lines of OpenSearch network policies.


# Output the S3 Bucket name so we know where to upload our Python data
output "s3_bucket_name" {
  value = aws_s3_bucket.hr_data_bucket.bucket
}

# Add this to the bottom of main.tf
resource "aws_iam_role_policy" "kb_embedding_policy" {
  name = "BedrockKBEmbeddingAndVectorAccess"
  role = aws_iam_role.knowledge_base_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Allow the Knowledge Base to use the Titan model to create embeddings
        Action   = ["bedrock:InvokeModel"]
        Effect   = "Allow"
        Resource = ["arn:aws:bedrock:us-east-1::foundation-model/*"]
      },
      {
        # Allow the Knowledge Base to write the vectors to the Database
        Action   = ["aoss:APIAccessAll"]
        Effect   = "Allow"
        Resource = ["*"]
      }
    ]
  })
}