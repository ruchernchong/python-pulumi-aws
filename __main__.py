import pulumi
import pulumi_archive as archive
import pulumi_aws as aws

assume_role = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[
                aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                    type="Service", identifiers=["lambda.amazonaws.com"]
                ),
            ],
            actions=["sts:AssumeRole"],
        )
    ]
)

iam_for_lambda = aws.iam.Role(
    "iam-for-lambda", name="iam-for-lambda", assume_role_policy=assume_role.json
)

lambda_ = archive.get_file(
    type="zip", source_file="index.py", output_path="package.zip"
)

function = aws.lambda_.Function(
    "python-pulumi-aws",
    code=pulumi.FileArchive("package.zip"),
    name="python-pulumi-aws",
    role=iam_for_lambda.arn,
    handler="index.handler",
    source_code_hash=lambda_.output_base64sha256,
    runtime=aws.lambda_.Runtime.PYTHON3D12,
)


pulumi.export("function_id", function.id)
pulumi.export("function_arn", function.arn)
