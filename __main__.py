import pulumi
import pulumi_archive as archive
import pulumi_aws as aws
import json

project_name = "python-pulumi-aws"


role = aws.iam.Role(
    f"{project_name}-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
    tags={"pulumi:stack": "dev", "pulumi:app": project_name},
)


aws.iam.RolePolicyAttachment(
    f"{project_name}-policy",
    role=role.name,
    policy_arn=aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
)

package = archive.get_file(
    type="zip", source_file="index.py", output_path="package.zip"
)

lambda_function = aws.lambda_.Function(
    f"{project_name}-function",
    code=pulumi.FileArchive("package.zip"),
    role=role.arn,
    handler="index.handler",
    source_code_hash=package.output_base64sha256,
    runtime=aws.lambda_.Runtime.PYTHON3D12,
)

# AWS has some really weird cron expression
event_rule = aws.cloudwatch.EventRule(
    f"{project_name}-rule",
    schedule_expression="cron(0/1 * * * ? *)",
    state="DISABLED",
)

event_target = aws.cloudwatch.EventTarget(
    f"{project_name}-target", rule=event_rule.name, arn=lambda_function.arn
)


pulumi.export("function_id", lambda_function.id)
pulumi.export("function_arn", lambda_function.arn)
