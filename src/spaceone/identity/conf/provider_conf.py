DEFAULT_PROVIDERS = [{
    'provider': 'aws',
    'name': 'AWS',
    'template': {
        'service_account': {
            'schema': {
                'type': 'object',
                'properties': {
                    'account_id': {
                        'title': 'Account ID',
                        'type': 'string',
                        'minLength': 4
                    }
                },
                'required': ['account_id']
            }
        }
    },
    'metadata': {
        'view': {
            'layouts': {
                'help:service_account:create': {
                    'name': 'Creation Help',
                    'type': 'markdown',
                    'options': {
                        'markdown': {
                            'en': (
                                '### Finding Your AWS Account ID\n'
                                'You can find your account ID in the AWS Management Console, or using the AWS CLI or AWS API.\n'
                                '#### Finding your account ID (Console)\n'
                                'In the navigation bar, choose **Support**, and then **Support Center**. '
                                'Your currently signed-in 12-digit account number (ID) appears in the **Support Center** title bar.\n'
                                '#### Finding your account ID (AWS CLI)\n'
                                'To view your user ID, account ID, and your user ARN:\n'
                                '- [aws sts get-caller-identity](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html)\n\n'
                                '#### Finding your account ID (AWS API)\n'
                                'To view your user ID, account ID, and your user ARN:\n'
                                '- [GetCallerIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html)\n\n'
                                '#### References\n'
                                '- [AWS Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html)\n'
                            )
                        }
                    }
                }
            }
        }
    },
    'capability': {
        'supported_schema': ['aws_access_key', 'aws_assume_role']
    },
    'tags': {
        'color': '#FF9900',
        'icon': 'https://assets-console-cloudone-stg.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws.svg',
        'external_link_template': 'https://{{data.account_id}}.signin.aws.amazon.com/console'
    }
}, {
    'provider': 'google_cloud',
    'version': 'v1',
    'name': 'Google Cloud',
    'template': {
        'service_account': {
            'schema': {
                'type': 'object',
                'properties': {
                    'sa_name': {
                        'title': 'Service Account',
                        'type': 'string',
                        'minLength': 4
                    },
                    'project_id': {
                        'title': 'Project ID',
                        'type': 'string',
                        'minLength': 4
                    }
                },
                'required': ['sa_name', 'project_id']
            }
        }
    },
    'capability': {
        'supported_schema': ['google_api_key', 'google_oauth_client_id']
    },
    'tags': {
        'color': '#4285F4',
        'icon': 'https://assets-console-cloudone-stg.s3.ap-northeast-2.amazonaws.com/console-assets/icons/google_cloud.svg'
    }
}, {
    'provider': 'azure',
    'name': 'Microsoft Azure',
    'template': {
        'service_account': {
            'schema': {
                'type': 'object',
                'properties': {
                    'tenant_id': {
                        'title': 'Tenant ID',
                        'type': 'string',
                        'minLength': 4
                    },
                    'subscription_id': {
                        'title': 'Subscription ID',
                        'type': 'string',
                        'minLength': 4
                    }
                },
                'required': ['tenant_id', 'subscription_id']
            }
        }
    },
    'capability': {
        'supported_schema': ['azure_client_secret']
    },
    'tags': {
        'color': '#00BCF2',
        'icon': 'https://assets-console-cloudone-stg.s3.ap-northeast-2.amazonaws.com/console-assets/icons/azure.svg'
    }
}]

aws_access_key = {
    'name': 'aws_access_key',
    'service_type': 'secret.credentials',
    'schema': {
        'required': [
            'aws_access_key_id',
            'aws_secret_access_key'
        ],
        'properties': {
            'aws_access_key_id': {
                'title': 'AWS Access Key',
                'type': 'string',
                'minLength': 4
            },
            'region_name': {
                'title': 'Region',
                'type': 'string',
                'minLength': 4,
                'examples': [
                    'ap-northeast-2'
                ]
            },
            'aws_secret_access_key': {
                'type': 'string',
                'minLength': 4,
                'title': 'AWS Secret Key'
            }
        },
        'type': 'object'
    },
    'labels': ['AWS'],
    'tags': {
        'description': 'AWS Access Key'
    }
}

aws_assume_role = {
    'name': 'aws_assume_role',
    'service_type': 'secret.credentials',
    'schema': {
        'required': [
            'aws_access_key_id',
            'aws_secret_access_key',
            'role_arn'
        ],
        'properties': {
            'role_arn': {
                'title': 'Role ARN',
                'type': 'string',
                'minLength': 4
            },
            'aws_access_key_id': {
                'title': 'AWS Access Key',
                'type': 'string',
                'minLength': 4
            },
            'region_name': {
                'title': 'Region',
                'type': 'string',
                'minLength': 4,
                'examples': [
                    'ap-northeast-2'
                ]
            },
            'aws_secret_access_key': {
                'type': 'string',
                'minLength': 4,
                'title': 'AWS Secret Key'
            }
        },
        'type': 'object'
    },
    'labels': ['AWS', 'Assume Role'],
    'tags': {
        'description': 'AWS Assume Role'
    }
}

google_api_key = {
    'name': 'google_api_key',
    'service_type': 'secret.credentials',
    'schema': {
        'required': [
            'api_key'
        ],
        'properties': {
            'api_key': {
                'title': 'API Key',
                'type': 'string',
                'minLength': 4
            }
        },
        'type': 'object'
    },
    'labels': ['Google Cloud', 'GCP'],
    'tags': {
        'description': 'Google API Key'
    }
}

google_oauth_client_id = {
    'name': 'google_oauth_client_id',
    'service_type': 'secret.credentials',
    'schema': {
        'properties': {
            'auth_provider_x509_cert_url': {
                'title': 'Auth Provider Cert URL',
                'type': 'string',
                'minLength': 4,
                'default': 'https://www.googleapis.com/oauth2/v1/certs'
            },
            'client_id': {
                'title': 'Client ID',
                'type': 'string',
                'minLength': 4,
                'examples': [
                    '10118252.....'
                ]
            },
            'token_uri': {
                'type': 'string',
                'minLength': 4,
                'default': 'https://oauth2.googleapis.com/token',
                'title': 'Token URI'
            },
            'zone': {
                'type': 'string',
                'minLength': 4,
                'examples': [
                    'asia-northeast3'
                ],
                'title': 'Region'
            },
            'client_x509_cert_url': {
                'type': 'string',
                'minLength': 4,
                'examples': [
                    'https://www.googleapis.com/...'
                ],
                'title': 'client_x509_cert_url'
            },
            'project_id': {
                'type': 'string',
                'minLength': 4,
                'examples': [
                    'project-id'
                ],
                'title': 'Project ID'
            },
            'private_key_id': {
                'type': 'string',
                'minLength': 4,
                'examples': [
                    '771823abcd...'
                ],
                'title': 'Private Key ID'
            },
            'auth_uri': {
                'type': 'string',
                'minLength': 4,
                'default': 'https://acounts.google.com/o/oauth2/auth',
                'title': 'Auth URI'
            },
            'type': {
                'default': 'service_account',
                'title': 'Type',
                'type': 'string',
                'minLength': 4
            },
            'client_email': {
                'type': 'string',
                'minLength': 4,
                'exmaples': [
                    '<api-name>api@project-id.iam.gserviceaccount.com'
                ],
                'title': 'Client Email'
            },
            'private_key': {
                'type': 'string',
                'minLength': 4,
                'examples': [
                    '-----BEGIN'
                ],
                'title': 'Private Key'
            }
        },
        'type': 'object',
        'required': [
            'type',
            'project_id',
            'private_key_id',
            'private_key',
            'client_email',
            'client_id',
            'auth_uri',
            'token_uri',
            'auth_provider_x509_cert_url',
            'client_x509_cert_url'
        ]
    },
    'labels': ['Google Cloud', 'GCP', 'OAuth2.0'],
    'tags': {
        'description': 'Google OAuth Client ID'
    }
}

azure_client_secret = {
    'name': 'azure_client_secret',
    'service_type': 'secret.credentials',
    'schema': {
        'required': [
            'client_id',
            'client_secret',
            'tenant_id',
            'subscription_id'
        ],
        'properties': {
            'client_id': {
                'title': 'Client ID',
                'type': 'string',
                'minLength': 4
            },
            'client_secret': {
                'title': 'Client Secret',
                'type': 'string',
                'minLength': 4
            },
            'tenant_id': {
                'title': 'Tenant ID',
                'type': 'string',
                'minLength': 4
            },
            'subscription_id': {
                'title': 'Subscription ID',
                'type': 'string',
                'minLength': 4
            }
        },
        'type': 'object'
    },
    'labels': ['Azure'],
    'tags': {
        'description': 'Azure Client Secret'
    }
}
