DEFAULT_PROVIDERS = [{
    "provider": "aws",
    "name": "AWS",
    "order": 1,
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
        "general_service_account_schema": [
            "aws_assume_role"
        ],
        "trusted_service_account_schema": [
            "aws_access_key"
        ],
        "support_trusted_service_account": True,
        "supported_schema": [
            "aws_access_key"
        ]
    },
    "tags": {
        'color': '#FF9900',
        'icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws.svg',
        'external_link_template': 'https://<%- data.account_id %>.signin.aws.amazon.com/console'
    }
}, {
    "provider": "google_cloud",
    "version": "v1",
    "name": "Google Cloud",
    "order": 2,
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
                                "Generate Your JSON Service Account Key.\n"
                                "[Service Account Key](https://cloud.google.com/docs/authentication/getting-started)\n"
                            ),
                            "ko": (
                                "# Google Cloud 시작 가이드\n"
                                "## Project 정보 확인하기\n"
                                "프로젝트 명, 프로젝트 아이디, 프로젝트 번호 등의 프로젝트 정보 확인하기\n"
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
        "general_service_account_schema": [
            "google_cloud_project_id"
        ],
        "trusted_service_account_schema": [
            "google_oauth2_credentials"
        ],
        "support_trusted_service_account": True,
        "supported_schema": ["google_oauth2_credentials"]
    },
    "tags": {
        'color': '#4285F4',
        'icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/google_cloud.svg',
        'external_link_template': 'https://console.cloud.google.com/home/dashboard?project=<%- data.project_id %>',
        'label': 'Google'
    }
}, {
    "provider": "azure",
    "name": "Azure",
    "order": 3,
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
                                "[Azure Subscription Portal](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)\n"
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
                                "[Azure Subscription Portal](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)\n"
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
        "general_service_account_schema": [
            "azure_subscription_id"
        ],
        "trusted_service_account_schema": [
            "azure_credentials",
        ],
        "support_trusted_service_account": True,
        "supported_schema": ["azure_client_secret"]
    },
    "tags": {
        'color': '#00BCF2',
        'icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/azure.svg'
    }
}]