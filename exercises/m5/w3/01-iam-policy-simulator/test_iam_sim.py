"""Checks for iam_sim.py. Don't edit this file."""

import pytest

from iam_sim import Finding, evaluate, review

DEPLOY_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {"Sid": "PushImages", "Effect": "Allow", "Action": ["ecr:BatchCheckLayerAvailability", "ecr:PutImage", "ecr:UploadLayerPart"], "Resource": "arn:aws:ecr:ap-southeast-3:123456789012:repository/revoshop-api"},
        {"Sid": "EcrLogin", "Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*"},
        {"Sid": "Images", "Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject"], "Resource": "arn:aws:s3:::revoshop-images/products/*"},
        {"Sid": "NoProdDeletes", "Effect": "Deny", "Action": "s3:DeleteObject*", "Resource": "arn:aws:s3:::revoshop-images/*"},
    ],
}


@pytest.mark.parametrize(
    ("action", "resource", "expected"),
    [
        ("ecr:PutImage", "arn:aws:ecr:ap-southeast-3:123456789012:repository/revoshop-api", "Allow"),
        ("ECR:putimage", "arn:aws:ecr:ap-southeast-3:123456789012:repository/revoshop-api", "Allow"),
        ("ecr:PutImage", "arn:aws:ecr:ap-southeast-3:123456789012:repository/other", "ImplicitDeny"),
        ("ecr:GetAuthorizationToken", "*", "Allow"),
        ("s3:PutObject", "arn:aws:s3:::revoshop-images/products/7/main.webp", "Allow"),
        ("s3:PutObject", "arn:aws:s3:::revoshop-images/Products/7/main.webp", "ImplicitDeny"),
        ("s3:DeleteObject", "arn:aws:s3:::revoshop-images/products/7/main.webp", "ExplicitDeny"),
        ("s3:DeleteObjectVersion", "arn:aws:s3:::revoshop-images/x", "ExplicitDeny"),
        ("ec2:TerminateInstances", "*", "ImplicitDeny"),
    ],
)
def test_actions_resources_and_deny_precedence(action, resource, expected):
    assert evaluate([DEPLOY_POLICY], action, resource) == expected


def test_deny_in_another_policy_wins_and_single_statement_object():
    admin = {"Statement": {"Effect": "Allow", "Action": "*", "Resource": "*"}}
    guard = {"Statement": [{"Effect": "Deny", "Action": ["iam:*", "organizations:*"], "Resource": "*"}]}
    assert evaluate([admin], "iam:CreateUser", "*") == "Allow"
    assert evaluate([admin, guard], "iam:CreateUser", "*") == "ExplicitDeny"
    assert evaluate([admin, guard], "ec2:RunInstances", "*") == "Allow"
    assert evaluate([], "s3:ListBucket", "*") == "ImplicitDeny"


def test_not_action_and_not_resource():
    deny_without_mfa = {
        "Statement": [
            {"Effect": "Allow", "Action": "*", "Resource": "*"},
            {"Effect": "Deny", "NotAction": ["iam:ChangePassword", "iam:*MFADevice*", "sts:GetSessionToken"], "Resource": "*", "Condition": {"BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}}},
        ]
    }
    assert evaluate([deny_without_mfa], "ec2:RunInstances", "*", {"aws:MultiFactorAuthPresent": False}) == "ExplicitDeny"
    assert evaluate([deny_without_mfa], "ec2:RunInstances", "*", {}) == "ExplicitDeny", "IfExists: missing key passes, so the Deny applies"
    assert evaluate([deny_without_mfa], "iam:EnableMFADevice", "*", {"aws:MultiFactorAuthPresent": False}) == "Allow"
    assert evaluate([deny_without_mfa], "ec2:RunInstances", "*", {"aws:MultiFactorAuthPresent": True}) == "Allow"

    except_prod = {"Statement": [{"Effect": "Allow", "Action": "rds:DeleteDBInstance", "NotResource": "arn:aws:rds:*:*:db:*-prod"}]}
    assert evaluate([except_prod], "rds:DeleteDBInstance", "arn:aws:rds:ap-southeast-3:123456789012:db:revoshop-staging") == "Allow"
    assert evaluate([except_prod], "rds:DeleteDBInstance", "arn:aws:rds:ap-southeast-3:123456789012:db:revoshop-prod") == "ImplicitDeny"


def test_conditions():
    policy = {
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "ssm:GetParameter*",
                "Resource": "arn:aws:ssm:*:*:parameter/revoshop/*",
                "Condition": {
                    "StringEquals": {"aws:RequestedRegion": ["ap-southeast-3", "ap-southeast-1"]},
                    "IpAddress": {"aws:SourceIp": "203.0.113.0/24"},
                    "NumericLessThan": {"aws:MultiFactorAuthAge": "3600"},
                },
            },
            {"Effect": "Allow", "Action": "ec2:StartInstances", "Resource": "*", "Condition": {"StringLike": {"aws:ResourceTag/Env": "stag*"}, "StringNotEquals": {"aws:PrincipalTag/Team": "contractors"}}},
            {"Effect": "Allow", "Action": "s3:ListBucket", "Resource": "*", "Condition": {"NumericGreaterThanEquals": {"s3:max-keys": "10"}, "DateGreaterThan": {"aws:CurrentTime": "2020-01-01T00:00:00Z"}}},
        ]
    }
    ok = {"aws:requestedregion": "ap-southeast-3", "aws:SourceIp": "203.0.113.25", "aws:MultiFactorAuthAge": 120}
    param = "arn:aws:ssm:ap-southeast-3:123456789012:parameter/revoshop/prod/jwt"
    assert evaluate([policy], "ssm:GetParameters", param, ok) == "Allow"
    assert evaluate([policy], "ssm:GetParameters", param, {**ok, "aws:RequestedRegion": "us-east-1"}) == "ImplicitDeny"
    assert evaluate([policy], "ssm:GetParameters", param, {**ok, "aws:SourceIp": "198.51.100.7"}) == "ImplicitDeny"
    assert evaluate([policy], "ssm:GetParameters", param, {**ok, "aws:MultiFactorAuthAge": 7200}) == "ImplicitDeny"
    del ok["aws:MultiFactorAuthAge"]
    assert evaluate([policy], "ssm:GetParameters", param, ok) == "ImplicitDeny", "missing key fails without IfExists"

    assert evaluate([policy], "ec2:StartInstances", "*", {"aws:ResourceTag/Env": "staging", "aws:PrincipalTag/Team": "backend"}) == "Allow"
    assert evaluate([policy], "ec2:StartInstances", "*", {"aws:ResourceTag/Env": "Staging", "aws:PrincipalTag/Team": "backend"}) == "ImplicitDeny"
    assert evaluate([policy], "ec2:StartInstances", "*", {"aws:ResourceTag/Env": "staging", "aws:PrincipalTag/Team": "contractors"}) == "ImplicitDeny"
    assert evaluate([policy], "s3:ListBucket", "*", {"s3:max-keys": 50, "aws:CurrentTime": "2026-09-15T00:00:00Z"}) == "ImplicitDeny", "unknown operator → not applied"


def test_review_flags_dangerous_grants():
    policy = {
        "Statement": [
            {"Sid": "Admin", "Effect": "Allow", "Action": "*", "Resource": "*"},
            {"Effect": "Allow", "Action": ["iam:PassRole", "ecs:RunTask"], "Resource": "*"},
            {"Sid": "Everything", "Effect": "Allow", "NotAction": "iam:*", "Resource": "*"},
            {"Sid": "Buckets", "Effect": "Allow", "Action": ["s3:*"], "Resource": "arn:aws:s3:::revoshop-images/*"},
            {"Sid": "ReadOnly", "Effect": "Allow", "Action": ["ec2:DescribeInstances", "s3:ListAllMyBuckets", "ssm:GetParameter"], "Resource": "*"},
            {"Sid": "Guard", "Effect": "Deny", "Action": "*", "Resource": "*"},
        ]
    }
    assert review(policy) == [
        Finding("Admin", "high", review(policy)[0].message),
        Finding("#1", "high", review(policy)[1].message),
        Finding("#1", "medium", review(policy)[2].message),
        Finding("Everything", "high", review(policy)[3].message),
        Finding("Buckets", "medium", review(policy)[4].message),
    ]
    assert all(f.message for f in review(policy))
    assert review(DEPLOY_POLICY) == []
