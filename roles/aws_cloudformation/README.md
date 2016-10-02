# Yellow NZ AWS CloudFormation Role

This is an Ansible role for generating CloudFormation templates and deploying CloudFormation stacks to Amazon Web Services.

## Requirements

- Ansible 2.1 or greater
- Boto (**pip install boto**)
- Boto3 (**pip install boto3**)
- openssl
- jq
- AWS CLI (**pip install awscli**)
- [Your local environment must be setup appropriately for working with AWS](https://connectmekiwi.atlassian.net/wiki/display/YPC/Installation+and+Configuration+of+the+AWS+Local+Environment)

## Setup

The recommended approach to use this role is to add this repository as a Git submodule to your Ansible playbook project.  

The submodule should be placed in the folder **roles/aws_cloudformation**, and can then be referenced from your playbooks as a role called `aws_cloudformation`.

You should also checkout the specific release required for your project.

```
$ git submodule add git@bitbucket.org:yellownz/aws_cloudformation.git roles/aws_cloudformation
Submodule path 'roles/aws_cloudformation': checked out '05f584e53b0084f1a2a6a24de6380233768a1cf0'
$ cd roles/aws_cloudformation
roles/aws_cloudformation$ git checkout 1.0
roles/aws_cloudformation$ cd ../..
$ git commit -a -m "Added aws_cloudformation 1.0 role"
```

### Role Updates

If you add this role as a submodule, you can update to later versions of this role by updating your submodules:

```
$ git submodule update --remote roles/aws_cloudformation
$ cd roles/aws_cloudformation
roles/aws_cloudformation$ git checkout 1.1
roles/aws_cloudformation$ cd ../..
$ git commit -a -m "Updated to aws_cloudformation 1.1 role"
```

## Usage

This role is designed to be used with Yellow NZ CloudFormation stacks and as such relies a single top-level variable:

- `stack` - defines the CloudFormation stack.  

Invoking this role will generate a folder called `build` in the current working directory, along with a timestamped folder of the current date (e.g. `./build/20160705154440/`).  Inside this folder the following files are created:

- `standard.yml` - the generated CloudFormation template in human readable YAML format.
- `standard.json` - the generated CloudFormation template in compact JSON format.  This is the template that is uploaded to the AWS CloudFormation service when creating or updating a stack.
- `policy.json` - the stack policy JSON file that is uploaded to the AWS CloudFormation service.

### S3 Template Upload

The S3 template upload feature is enabled by default, but can be disabled if required by setting the variable `cf_upload_se` to `false`.

The `standard.json` template will also be uploaded to an S3 bucket as defined by the variable `cf_s3_bucket`.  

If not specified, `cf_s3_bucket` is set using the `cf_s3_bucket_mappings` dictionary, based upon on the account of the user executing this role:

```
cf_s3_bucket_mappings:
  "706286425777": dev-ytech-cloudformation-templates
  "801225830213": prod-ytech-cloudformation-templates
  "847222289464": sandbox-ytech-cloudformation-templates
  "639534165454": dr-ytech-cloudformation-templates
```

The `standard.json` template will be placed in the following path in S3:

`<s3-bucket-name>/<stack-name>/<timestamp>/standard.json`

For example:

`dev-ytech-cloudformation-templates/dev-yellowsem/20160705154440/standard.json`

### Generating a Template Only

You can generate a template only by passing the tag `generate` to this role.  This will only create the templates as described above, but not attempt to create or update the stack in CloudFormation.

`ansible-playbook site.yml -e env=dev --tags generate`

Note the generated template will be uploaded to S3 as described earlier.

### Temporarily Disabling Stack Policy

You can temporarily disable the stack policy for a provisioning run by setting the variable `cf_disable_stack_policy` to true:

`ansible-playbook site.yml -e env=prod -e cf_disable_stack_policy=true`

This will set to the stack policy to the following policy before stack modification:

```
{
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : "Update:*",
        "Principal": "*",
        "Resource" : "*"
      }
    ]
  }
```

And then after stack modification is complete, reset the stack policy to it's previous state.  

> Note: This role will also reset the stack policy in the event of a stack modification failure

## Role Facts

This role sets the following facts that you can use subsequently in your roles:

- `cf_stack_result` - the raw return result of the Ansible cloudformation module
- `cf_stack_facts` - the raw return result of the Ansible cloudformation_facts module
- `cf_stack_resources` - dictionary of all stack resources with key set to logical resource ID and value set to physical resource ID
- `cf_stack_outputs` - dictionary of all stack outputs with key set to output parameter name and value set to output parameter value
- `cf_s3_template_url` - S3 URL of the CloudFormation template.  This is also printed at the end of the completion of this role.
- `cf_cost_estimate_url` - Cost Calculator URL for cost estimate of the generated CloudFormation template.  This is also printed at the end of the completion of this role.  Note you must set the variables `cf_calculate_costs` and `cf_upload_s3` to `true` for a cost estimate to be generated.

## Examples

### Defining the Stack

See the included [`sample.yml`](sample.yml) file for an example stack definition.

### Invoking the Role

The following is an example of a playbook configured to use this role.  Note the use of the [Yellow NZ STS role](https://bitbucket.org/yellownz/aws_sts.git) to obtain STS credentials is separate from this role.

```
---
- name: STS Assume Role Playbook
  hosts: "{{ env }}"
  gather_facts: no
  environment:
    AWS_DEFAULT_REGION: "{{ lookup('env', 'AWS_DEFAULT_REGION') | default('ap-southeast-2', true) }}"
  roles:
  - aws_sts

- name: Stack Deployment Playbook
  hosts: "{{ env }}"
  environment: "{{ sts_creds }}"
  roles:
    - aws_cloudformation
```

## Release Notes

### Version 1.3.8

- ** ENHANCEMENT **: Add Elastic IP support for EC2 instances

### Version 1.3.7

- ** ENHANCEMENT **: Support IP-based access policies for Elasticsearch domains

### Version 1.3.6

- ** BUG FIX **: Add missing Lambda mappings for yellow-sandbox

### Version 1.3.5

- ** BREAKING CHANGE **: Remove AcmCloudfront custom resources now that CloudFormation natively supports ACM

### Version 1.3.4

- ** BUG FIX **: Make ELB security group rules respect conditional listener creation

### Version 1.3.3

- ** ENHANCEMENT **: Support conditional creation of ELB listeners

### Version 1.3.2

- ** BUG FIX **: Fix delete stack logic

### Version 1.3.1

- ** BUG FIX **: Add dependencies to ensure correct orchestration of Sumologic provisioner resources
- ** ENHANCEMENT **: Add ability to specify S3 object versions for Log Group, Log Provisioner and Collector Lambda functions
- ** ENHANCEMENT **: Add support for custom EC2 log groups

### Version 1.3.0

- ** NEW FEATURE **: Support for Cloudwatch Logs and Sumologic Sources

### Version 1.2.20

- ** BUG FIX **: Update cloudformation_facts module to return all resources when > 100 exist

### Version 1.2.19

- ** ENHANCEMENT **: Add create parameter for ECS tasks

### Version 1.2.18

- ** ENHANCEMENT **: Add support for ACM certificates in CloudFront distributions

### Version 1.2.17

- ** ENHANCEMENT **: Add support for IAM roles

### Version 1.2.16

- ** ENHANCEMENT **: Add support for list style generic resources (supports conditional create parameter) 
- ** ENHANCEMENT **: Add conditional create parameter to Lambda function resources

### Version 1.2.15

- ** BUG FIX **: Honour create configuration parameter in Cloudwatch alarms
- ** BUG FIX **: Allow empty subscriptions for Cloudwatch SNS topics

### Version 1.2.14

- ** ENHANCEMENT **: Make Elasticsearch custom policies work with multiple principals

### Version 1.2.13

- ** ENHANCEMENT **: Make S3 bucket names optional

### Version 1.2.12

- ** BUG FIX **: Update ecsBase AMI with embedded proxy for cloud-init operations

### Version 1.2.11

- ** ENHANCEMENT **: Add Newmarket IP addresses

### Version 1.2.10

- ** BUG FIX **: Add ecs:StartTelemetrySession privilege to EC2 instance roles

### Version 1.2.9

- ** ENHANCEMENT **: Allow Spring subnets as default ICMP

### Version 1.2.8

- ** BUG FIX **: Fix support for Lambda resources

### Version 1.2.7

- ** ENHANCEMENT **: Allow empty user lists when defining S3 bucket policies

### Version 1.2.6

- ** ENHANCEMENT **: Add support for custom policies on Elasticsearch domains

### Version 1.2.5

- ** BUG FIX **: Ensure role errors are not suppressed by rescue action
- ** ENHANCEMENT **: Make S3, CloudFront, WAF creation conditional on create attribute

### Version 1.2.4

- ** ENHANCEMENT **: Add support for CloudFront DNS aliases

### Version 1.2.3

- ** BREAKING CHANGE **: Restrict S3 read-only users to getting objects, not listing buckets

### Version 1.2.2

- ** BUG FIX **: Add SNS topic dependencies for CloudWatch alarms

### Version 1.2.1

- ** ENHANCEMENT **: Disable OK Actions alarm action for ELB and DynamoDB CloudWatch alarms

### Version 1.2.0

- ** NEW FEATURE **: Add support for CloudWatch alarms

### Version 1.1.3

- ** ENHANCEMENT **: Make RDS `security_groups` property additive to generate security groups

### Version 1.1.2

- ** ENHANCEMENT **: Add `cf_upload_s3` variable to enable/disable S3 template uploads

### Version 1.1.1

- ** BUG FIX **: Use Amazon-provided policy for ECS service roles, fixes ELB redeployment issue

### Version 1.1.0

- ** NEW FEATURE **: Upload CloudFormation templates to S3
- ** NEW FEATURE **: Generate Cost Calculator URL for cost estimate
- ** NEW FEATURE **: Add support for CloudFront and WAF

### Version 1.0.0

- First release
- **DEPRECATED**: `cf_configure_stack` no longer required to create or modify a stack
- **DEPRECATED**: Credstash provisioning external from CloudFormation is no longer supported
- **DEPRECATED**: ECS provisioning external from CloudFormation is no longer supported
