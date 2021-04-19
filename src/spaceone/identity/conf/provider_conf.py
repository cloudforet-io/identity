DEFAULT_PROVIDERS = [{
    "provider": "aws",
    "name": "AWS",
    "template": {
        "service_account": {
            "schema": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "title": "Account ID",
                        "type": "string",
                        "minLength": 4
                    }
                },
                "required": ["account_id"]
            }
        }
    },
    "metadata": {
        "view": {
            "layouts": {
                "help:service_account:create": {
                    "name": "Creation Help",
                    "type": "markdown",
                    "options": {
                        "markdown": {
                            "en": (
                                "# Help for AWS Users\n"
                                "## Find Your AWS Account ID\n"
                                "Get your AWS Account ID.\n"
                                "[AWS Account ID](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html)\n"
                                "## Get Your Assume role\n"
                                "Granting permissions to create temporary security credentials.\n"
                                "[AWS Assume Role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_permissions-to-switch.html)\n"
                                "## Issue AWS Access Key \n"
                                "Get your AWS Access Key & AWS Secret Key\n"
                                "[AWS Access Key & AWS Secret Key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)\n"
                            ),
                            "ko": (
                                "# AWS 이용자 가이드\n"
                                "## AWS 어카운트 아이디(Account ID) 찾기\n"
                                "사용자의 AWS 어카운트 아이디 AWS 콘솔(Console)에서 확인하기\n"
                                "[AWS Account ID](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/console_account-alias.html)\n"
                                "## Assume role 획득하기\n"
                                "임시 보안 자격증명을 만들 수있는 권한을 부여하기.\n"
                                "[AWS Assume Role](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_roles_use_permissions-to-switch.html)\n"
                                "## AWS Access Key 발급하기\n"
                                "AWS Access Key & AWS Secret Key 발급하기\n"
                                "[AWS Access Key & AWS Secret Key](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)\n"
                            ),

                        }
                    }
                }
            }
        }
    },
    "capability": {
        "supported_schema": ["aws_access_key", "aws_assume_role"]
    },
    "tags": [
        {
            'key': 'color',
            'value': '#FF9900'
        }, {
            'key': 'icon',
            'value': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws.svg'
        }, {
            'key': 'external_link_template',
            'value': 'https://<%- data.account_id %>.signin.aws.amazon.com/console'
        }
    ]
}, {
    "provider": "google_cloud",
    "version": "v1",
    "name": "Google Cloud",
    "template": {
        "service_account": {
            "schema": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "title": "Project ID",
                        "type": "string",
                        "minLength": 4
                    }
                },
                "required": ["project_id"]
            }
        }
    },
    "metadata": {
        "view": {
            "layouts": {
                "help:service_account:create": {
                    "name": "Creation Help",
                    "type": "markdown",
                    "options": {
                        "markdown": {
                            "en": (
                                "# Getting started with Google Cloud\n"
                                "## Identifying Your Project\n"
                                "Get your Project infos (Project Name, Project ID and Project number)\n"
                                "[Project Info](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)\n"
                                "## Get Your Service Account Key(JSON)\n"
                                "Generate Your a JSON Service Account Key.\n"
                                "[Service Account Key](https://cloud.google.com/docs/authentication/getting-started)\n"
                            ),
                            "ko": (
                                "# Google Cloud 시작 가이드\n"
                                "## Project 정보 확인하기\n"
                                "프로젝트 명, 프로젝트 아이디 프로젝트 번호등등의 프로젝트 정보 확인하기\n"
                                "[Project Info](https://cloud.google.com/resource-manager/docs/creating-managing-projects?hl=ko#identifying_projects)\n"
                                "## 서비스 어카운트 키(JSON) 받기\n"
                                "JSON 포멧의 서비스 어카운트 키를 생성하기.\n"
                                "[Service Account Key](https://cloud.google.com/docs/authentication/getting-started?hl=ko)\n"
                            ),

                        }
                    }
                }
            }
        }
    },
    "capability": {
        "supported_schema": ["google_oauth2_credentials"]
    },
    "tags": [
        {
            'key': 'color',
            'value': '#4285F4'
        }, {
            'key': 'icon',
            'value': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/google_cloud.svg'
        }, {
            'key': 'external_link_template',
            'value': 'https://console.cloud.google.com/home/dashboard?project=<%- data.project_id %>'
        }
    ]
}, {
    "provider": "azure",
    "name": "Microsoft Azure",
    "template": {
        "service_account": {
            "schema": {
                "type": "object",
                "properties": {
                    "tenant_id": {
                        "title": "Tenant ID",
                        "type": "string",
                        "minLength": 4
                    },
                    "subscription_id": {
                        "title": "Subscription ID",
                        "type": "string",
                        "minLength": 4
                    }
                },
                "required": ["tenant_id", "subscription_id"]
            }
        }
    },
    "metadata": {
        "view": {
            "layouts": {
                "help:service_account:create": {
                    "name": "Creation Help",
                    "type": "markdown",
                    "options": {
                        "markdown": {
                            "en": (
                                "# Help for Azure Users\n"
                                "## Find Your Azure Subscription ID\n"
                                "Azure Subscription ID via CLI.\n"
                                "[Azure Subscription CLI](https://docs.microsoft.com/en-us/cli/azure/ext/account/account/subscription?view=azure-cli-latest)\n"
                                "Azure Subscription ID via PowerShell.\n"
                                "[Azure Subscription PowerShell](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-authenticate-service-principal-powershell)\n"
                                "Create Azure Subscription via Portal.\n"
                                "[Azure Subscription Portal(https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)\n"
                                "## Find Your Azure Tenant ID\n"
                                "Azure Tenant ID via CLI.\n"
                                "[Azure Tenant CLI](https://docs.microsoft.com/en-us/cli/azure/ext/account/account/tenant?view=azure-cli-latest)\n"
                                "Azure Tenant ID via PowerShell.\n"
                                "[Azure Tenant PowerShell](https://docs.microsoft.com/en-us/powershell/module/az.accounts/get-aztenant?view=azps-5.0.0)\n"
                                "## Get Your Client Secret and ID\n"
                                "Check Client Secret via Portal.\n"
                                "[Azure Client Secret Portal](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)\n"
                            ),
                            "ko": (
                                "# Azure 이용자 가이드\n"
                                "## Azure 구독 아이디(Subscription ID) 찾기\n"
                                "CLI에서 사용자의 구독 아이디 확인하기.\n"
                                "[Azure Subscription CLI](https://docs.microsoft.com/en-us/cli/azure/ext/account/account/subscription?view=azure-cli-latest)\n"
                                "PowerShell에서 사용자의 구독 아이디 확인하기.\n"
                                "[Azure Subscription PowerShell](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-authenticate-service-principal-powershell)\n"
                                "포털에서 사용자의 구독 아이디 확인하기.\n"
                                "[Azure Subscription Portal(https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)\n"
                                "## Azure 테넌트 아이디(Tenant ID) 찾기\n"
                                "CLI에서 사용자의 테넌트 아이디 확인하기.\n"
                                "[Azure Tenant CLI](https://docs.microsoft.com/en-us/cli/azure/ext/account/account/tenant?view=azure-cli-latest)\n"
                                "PowerShell에서 사용자의 테넌트 아이디 확인하기.\n"
                                "[Azure Tenant PowerShell](https://docs.microsoft.com/en-us/powershell/module/az.accounts/get-aztenant?view=azps-5.0.0)\n"
                                "## 사용자의 클라이언트 시크릿 정보(Client Secret&ID) 가져오기\n"
                                "포털에서 사용자의 클라이언트 시크릿 정보 확인하기.\n"
                                "[Azure Client Secret Portal](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)\n"
                            ),

                        }
                    }
                }
            }
        }
    },
    "capability": {
        "supported_schema": ["azure_client_secret"]
    },
    "tags": [
        {
            'key': 'color',
            'value': '#00BCF2'
        }, {
            'key': 'icon',
            'value': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/azure.svg'
        }
    ]
}, {
    "provider": "spaceone",
    "name": "SpaceONE",
    "template": {
        "service_account": {
            "schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "title": "User ID",
                        "type": "string",
                        "minLength": 4
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    "capability": {
        "supported_schema": ["spaceone_api_key"]
    },
    "tags": [
        {
            'key': 'color',
            'value': '#6638B6'
        }, {
            'key': 'icon',
            'value': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/spaceone.svg'
        }
    ]
}, {
    "provider": "alibaba_cloud",
    "name": "Alibaba Cloud",
    "template": {
        "service_account": {
            "schema": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "title": "Account ID",
                        "type": "string",
                        "minLength": 4
                    }
                },
                "required": ["account_id"]
            }
        }
    },
    "metadata": {
        "view": {
            "layouts": {
                "help:service_account:create": {
                    "name": "Creation Help",
                    "type": "markdown",
                    "options": {
                        "markdown": {
                            "en": (
                                "# Help for Alibaba Cloud Users\n"
                                "## Find Your Alibaba Cloud Account ID\n"
                                "Get your Alibaba Cloud Account ID.\n"
                                "Individual Account: Alibaba Cloud console > Click your avatar > Account Management Page > Security Settings > **Account ID**\nEnterprise Account: Alibaba Cloud console > Click your avatar > **Enterprise Alias**\n"
                                "## Generate Your AccessKey Pair\n"
                                "Get your Alibaba Cloud AccessKey ID & AccessKey Secret\n"
                                "[Alibaba Cloud AccessKey & AccessSecret](https://www.alibabacloud.com/help/doc-detail/53045.htm?spm=a2c63.p38356.879954.17.6be510df6F9vxS#concept-53045-zh)\n"
                            ),
                            "ko": (
                                "# 알리바바 클라우드 이용자 가이드\n"
                                "## 알리바바 클라우드 계정 아이디(Account ID) 찾기\n"
                                "콘솔에서 사용자의 알리바바 클라우드 계정 아이디 확인하기\n"
                                "개인 계정: 알리바바 클라우드 콘솔 > 사용자 아바타 클릭 > Account Management 페이지 > Security Settings > **Account ID**\n엔터프라이즈 계정: 알리바바 클라우드 콘솔 > 사용자 아바타 클 > **Enterprise Alias**\n"
                                "## 알리바바 클라우드 AccessKey Pair 발급하기\n"
                                "콘솔에서 알리바바 클라우드 AccessKey ID & AccessKey Secret 생성하기\n"
                                "[Alibaba Cloud AccessKey & AccessKey Secret](https://www.alibabacloud.com/help/doc-detail/53045.htm?spm=a2c63.p38356.879954.17.6be510df6F9vxS#concept-53045-zh)\n"
                            ),
                        }
                    }
                }
            }
        }
    },
    "capability": {
        "supported_schema": ["alibaba_cloud_access_key_pair"]
    },
    "tags": [
        {
            'key': 'color',
            'value': '#FF6A00'
        }, {
            'key': 'icon',
            'value': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/alibaba_cloud/logo.svg'
        }, {
            'key': 'external_link_template',
            'value': 'https://homenew-intl.console.aliyun.com/'
        }
    ]
}, {
    "provider": "oracle_cloud",
    "name": "Oracle Cloud Infrastructure",
    "template": {
        "service_account": {
            "schema": {
                "type": "object",
                "properties": {
                    "tenancy_name": {
                        "title": "Tenancy Name",
                        "type": "string",
                        "minLength": 4
                    },
                    "user_name": {
                        "title": "User Name",
                        "type": "string",
                        "minLength": 4
                    }
                },
                "required": ["tenancy_name", "user_name"]
            }
        }
    },
    "metadata": {
        "view": {
            "layouts": {
                "help:service_account:create": {
                    "name": "Creation Help",
                    "type": "markdown",
                    "options": {
                        "markdown": {
                            "en": (
                                "# Getting started with Oracle Cloud Intrastructure\n"
                                "## Find Your Tenancy & User OCID\n"
                                "[Get your User's OCID  and Tenancy's OCID](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#five)\n"
                                "## Generate RSA key pair and Key's Fingerprint\n"
                                "[Generate RSA key pair]([https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#two](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#two))\n"
                                "[Get Key's Fingerprint](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#four)\n"
                                "## Upload the Public Key from the key pair in the Console\n"
                                "[Upload Your Public Key](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#three)\n"
                                #R"## Note: It requires to add \n at end of every each line of your private_key string prior to put private key in credentials. ex) -----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0\n...\n..\n"
                                "## Note: You must copy and paste the private key, except for the header and footer of the private_key string, before putting it into Credential. The same is true for typing in JSON format; each string is separated by a space.\n"
                            ),
                            "ko": (
                                "# 오라클 클라우드 이용자 가이드\n"
                                "## 오라클 클라우드 테넌시와 유저 OCID 찾기\n"
                                "[유저와 테넌시 OCID 정보 확인](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#five)\n"
                                "## RSA 키 페어와 핑거프린트 생성\n"
                                "[RSA 키 페어 생성]([https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#two](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#two))\n"
                                "[핑거프린트 생성](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#four)\n"
                                "## 오라클 클라우드 콘솔에 공개 키 등록\n"
                                "[퍼블릭 키 업로드](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm#three)\n"
                                "## Note: 개인 키를 Credential에 넣기 전에 private_key 문자열의 헤더와 푸터를 제외하고 복사해서 붙여넣어야 합니다. JSON 형식으로 입력 시에도 동일하며, 각 문자열은 공백으로 구분합니다.\n  "
                            ),
                        }
                    }
                }
            }
        }
    },
    "capability": {
        "supported_schema": ["oci_api_key"]
    },
    "tags": [
        {
            'key': 'color',
            'value': '#D73A27'
        }, {
            'key': 'icon',
            'value': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/oci/ic_provider_oracle.svg'
        }, {
            'key': 'external_link_template',
            'value': 'https://www.oracle.com/kr/cloud/sign-in.html'
        }
    ]

}]

aws_access_key = {
    "name": "aws_access_key",
    "service_type": "secret.credentials",
    "schema": {
        "required": [
            "aws_access_key_id",
            "aws_secret_access_key"
        ],
        "properties": {
            "aws_access_key_id": {
                "title": "AWS Access Key",
                "type": "string",
                "minLength": 4
            },
            "aws_secret_access_key": {
                "type": "string",
                "minLength": 4,
                "title": "AWS Secret Key"
            }
        },
        "type": "object"
    },
    "labels": ["AWS"],
    "tags": [
        {
            'key': 'description',
            'value': 'AWS Access Key'
        }
    ]
}

aws_assume_role = {
    "name": "aws_assume_role",
    "service_type": "secret.credentials",
    "schema": {
        "required": [
            "aws_access_key_id",
            "aws_secret_access_key",
            "role_arn"
        ],
        "properties": {
            "role_arn": {
                "title": "Role ARN",
                "type": "string",
                "minLength": 4
            },
            "aws_access_key_id": {
                "title": "AWS Access Key",
                "type": "string",
                "minLength": 4
            },
            "aws_secret_access_key": {
                "type": "string",
                "minLength": 4,
                "title": "AWS Secret Key"
            }
        },
        "type": "object"
    },
    "labels": ["AWS", "Assume Role"],
    "tags": [
        {
            'key': 'description',
            'value': 'AWS Assume Role'
        }
    ]
}

google_api_key = {
    "name": "google_api_key",
    "service_type": "secret.credentials",
    "schema": {
        "required": [
            "api_key"
        ],
        "properties": {
            "api_key": {
                "title": "API Key",
                "type": "string",
                "minLength": 4
            }
        },
        "type": "object"
    },
    "labels": ["Google Cloud", "GCP"],
    "tags": [
        {
            'key': 'description',
            'value': 'Google API Key'
        }
    ]
}

google_oauth2_credentials = {
    "name": "google_oauth2_credentials",
    "service_type": "secret.credentials",
    "schema": {
        "required": [
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
            "client_id",
            "auth_uri",
            "token_uri",
            "auth_provider_x509_cert_url",
            "client_x509_cert_url"
        ],
        "properties": {
            "type": {
                "title": "Type",
                "type": "string",
                "minLength": 4,
                "default": "service_account"
            },
            "project_id": {
                "title": "Project ID",
                "type": "string",
                "minLength": 4
            },
            "private_key_id": {
                "title": "Private Key ID",
                "type": "string",
                "minLength": 4
            },
            "private_key": {
                "title": "Private Key",
                "type": "string",
                "minLength": 4
            },
            "client_email": {
                "title": "Client Email",
                "type": "string",
                "minLength": 4
            },
            "client_id": {
                "title": "Client ID",
                "type": "string",
                "minLength": 4
            },
            "auth_uri": {
                "title": "Auth URI",
                "type": "string",
                "minLength": 4,
                "default": "https://acounts.google.com/o/oauth2/auth"
            },
            "token_uri": {
                "title": "Token URI",
                "type": "string",
                "minLength": 4,
                "default": "https://oauth2.googleapis.com/token"
            },
            "auth_provider_x509_cert_url": {
                "title": "Auth Provider X509 Cert URL",
                "type": "string",
                "minLength": 4,
                "default": "https://www.googleapis.com/oauth2/v1/certs"
            },
            "client_x509_cert_url": {
                "title": "Client X509 Cert URL",
                "type": "string",
                "minLength": 4
            }
        },
        "type": "object"
    },
    "labels": ["Google Cloud", "GCP", "OAuth2.0"],
    "tags": [
        {
            'key': 'description',
            'value': 'Google OAuth2 Credentials'
        }
    ]
}

azure_client_secret = {
    "name": "azure_client_secret",
    "service_type": "secret.credentials",
    "schema": {
        "required": [
            "client_id",
            "client_secret",
            "tenant_id",
            "subscription_id"
        ],
        "properties": {
            "client_id": {
                "title": "Client ID",
                "type": "string",
                "minLength": 4
            },
            "client_secret": {
                "title": "Client Secret",
                "type": "string",
                "minLength": 4
            },
            "tenant_id": {
                "title": "Tenant ID",
                "type": "string",
                "minLength": 4
            },
            "subscription_id": {
                "title": "Subscription ID",
                "type": "string",
                "minLength": 4
            }
        },
        "type": "object"
    },
    "labels": ["Azure"],
    "tags": [
        {
            'key': 'description',
            'value': 'Azure Client Secret'
        }
    ]
}

spaceone_api_key = {
    "name": "spaceone_api_key",
    "service_type": "secret.credentials",
    "schema": {
        "required": [
            "api_key_id",
            "api_key",
            "endpoint"
        ],
        "properties": {
            "api_key_id": {
                "title": "API Key ID",
                "type": "string",
                "minLength": 4
            },
            "api_key": {
                "title": "API Key",
                "type": "string",
                "minLength": 4
            },
            "endpoint": {
                "title": "Identity Service Endpoint",
                "type": "string",
                "minLength": 4
            }
        },
        "type": "object"
    },
    "labels": ["SpaceONE"],
    "tags": [
        {
            'key': 'description',
            'value': 'SpaceONE API Key'
        }
    ]
}

alibaba_cloud_access_key_pair = {
    "name": "alibaba_cloud_access_key_pair",
    "service_type": "secret.credentials",
    "schema": {
        "required": [
            "ali_access_key_id",
            "ali_access_key_secret"
        ],
        "properties": {
            "ali_access_key_id": {
                "title": "Alibaba Cloud AccessKey ID",
                "type": "string",
                "minLength": 4
            },
            "ali_access_key_secret": {
                "title": "Alibaba Cloud AccessKey Secret",
                "type": "string",
                "minLength": 4
            }
        },
        "type": "object"
    },
    "labels": ["Alibaba"],
    "tags": [
        {
            'key': 'description',
            'value': "Alibaba Cloud AccessKey Pair"
        }
    ]
}

oci_api_key = {
    "name": "oci_api_key",
    "service_type": "secret.credentials",
    "schema": {
        "required": [
            "tenancy",
            "user",
            "key_content",
            "fingerprint"
        ],
        "properties": {
            "tenancy": {
                "title": "Tenancy's OCID",
                "type": "string",
                "minLength": 4
            },
            "user":{
                "title": "User's OCID",
                "type": "string",
                "minLength": 4
            },
            "key_content": {
                "title": "Private Key Content",
                "type": "string",
                "minLength": 4
            },
            "fingerprint": {
                "title": "Fingerprint",
                "type": "string",
                "minLength": 4
            }
        },
        "type": "object"
    },
    "labels": ["Oracle"],
    "tags": [
        {
            'key': 'description',
            'value': "Oracle Cloud Infrastructure Access Configuration"
        }
    ]
}
