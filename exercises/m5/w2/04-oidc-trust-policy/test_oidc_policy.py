"""Checks for oidc_policy.py. Don't edit this file."""

import copy

import pytest

from oidc_policy import allows, trust_policy

ISS = "https://token.actions.githubusercontent.com"


def claims(sub, aud="sts.amazonaws.com", iss=ISS):
    return {"iss": iss, "aud": aud, "sub": sub}


def test_policy_document():
    policy = trust_policy("123456789012", "sari", "revoshop", environments=["staging", "production"], branches=["main"])
    assert policy == {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"},
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": [
                            "repo:sari/revoshop:environment:staging",
                            "repo:sari/revoshop:environment:production",
                            "repo:sari/revoshop:ref:refs/heads/main",
                        ]
                    },
                },
            }
        ],
    }


@pytest.mark.parametrize(
    ("args", "kwargs"),
    [
        (("12345", "sari", "revoshop"), {"environments": ["production"]}),
        (("123456789012", "sari", "revoshop"), {}),
        (("123456789012", "*", "revoshop"), {"branches": ["main"]}),
        (("123456789012", "sari", "rev?shop"), {"branches": ["main"]}),
        (("123456789012", "sari", "revoshop"), {"environments": ["prod:uction"]}),
        (("123456789012", "sari", "revoshop"), {"branches": ["*"]}),
        (("123456789012", "", "revoshop"), {"branches": ["main"]}),
    ],
)
def test_rejects_unsafe_input(args, kwargs):
    with pytest.raises(ValueError):
        trust_policy(*args, **kwargs)


def test_who_can_assume_the_role():
    policy = trust_policy("123456789012", "sari", "revoshop", environments=["production"], branches=["main"])
    assert allows(policy, claims("repo:sari/revoshop:environment:production"))
    assert allows(policy, claims("repo:sari/revoshop:ref:refs/heads/main"))
    denied = [
        claims("repo:sari/revoshop:environment:staging"),
        claims("repo:sari/revoshop:ref:refs/heads/feature"),
        claims("repo:sari/revoshop:pull_request"),
        claims("repo:attacker/revoshop:environment:production"),
        claims("repo:sari/revoshop-fork:ref:refs/heads/main"),
        claims("repo:Sari/revoshop:environment:production"),
        claims("repo:sari/revoshop:environment:production", aud="https://github.com/sari"),
        claims("repo:sari/revoshop:environment:production", iss="https://evil.example.com"),
        {"iss": ISS, "aud": "sts.amazonaws.com"},
    ]
    for token in denied:
        assert not allows(policy, token), token


def test_evaluator_semantics():
    wide = trust_policy("123456789012", "sari", "revoshop", branches=["main"])
    wide["Statement"][0]["Condition"]["StringLike"]["token.actions.githubusercontent.com:sub"] = "repo:sari/*"
    assert allows(wide, claims("repo:sari/other-repo:pull_request")), "a wildcard really does trust every repo"
    single = copy.deepcopy(wide)
    single["Statement"][0]["Condition"]["StringLike"]["token.actions.githubusercontent.com:sub"] = "repo:sari/rev?shop:ref:refs/heads/main"
    assert allows(single, claims("repo:sari/revxshop:ref:refs/heads/main"))
    assert not allows(single, claims("repo:sari/revooshop:ref:refs/heads/main"))
    dots = copy.deepcopy(wide)
    dots["Statement"][0]["Condition"]["StringLike"]["token.actions.githubusercontent.com:sub"] = "repo:sari/rev.shop:*"
    assert not allows(dots, claims("repo:sari/revXshop:ref:refs/heads/main")), "'.' is literal, not a regex"

    unknown = copy.deepcopy(wide)
    unknown["Statement"][0]["Condition"]["ForAnyValue:StringLike"] = {"token.actions.githubusercontent.com:sub": "*"}
    assert not allows(unknown, claims("repo:sari/revoshop:ref:refs/heads/main"))

    denied_effect = copy.deepcopy(wide)
    denied_effect["Statement"][0]["Effect"] = "Deny"
    assert not allows(denied_effect, claims("repo:sari/revoshop:ref:refs/heads/main"))

    other_action = copy.deepcopy(wide)
    other_action["Statement"][0]["Action"] = ["sts:AssumeRole"]
    assert not allows(other_action, claims("repo:sari/revoshop:ref:refs/heads/main"))

    listed = copy.deepcopy(wide)
    listed["Statement"][0]["Action"] = ["sts:TagSession", "sts:AssumeRoleWithWebIdentity"]
    listed["Statement"][0]["Condition"]["StringEquals"]["token.actions.githubusercontent.com:aud"] = ["api://other", "sts.amazonaws.com"]
    assert allows(listed, claims("repo:sari/anything:ref:refs/heads/main"))
