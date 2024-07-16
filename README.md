# ASG AMI Report

This repository contains a Python script and a Jenkins pipeline configuration to generate a report of AWS Auto Scaling Groups (ASGs) and their associated Amazon Machine Images (AMIs). The report is generated in both JSON and CSV formats.

## Files

- `aws_report_script.py`: A Python script that generates a report of AWS Auto Scaling Groups and their AMIs.
- `Jenkinsfile`: A Jenkins pipeline configuration file to automate the execution of the Python script.

## Requirements

- Python 3.x
- Boto3 library
- AWS credentials with appropriate permissions to access EC2 and Auto Scaling resources

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/asg-ami-report.git
    cd asg-ami-report
    ```

2. Install the required Python packages:
    ```sh
    pip install boto3
    ```

3. Ensure your AWS credentials are set up. You can configure them using the AWS CLI:
    ```sh
    aws configure
    ```

## Running the Python Script

You can manually run the Python script to generate the report:

```sh
python3 aws_report_script.py
```
The script will generate JSON and CSV reports in the current directory or a directory specified by the REPORT_DIR environment variable.

## Jenkins Pipeline

The `Jenkinsfile` defines a Jenkins pipeline that automates the process of checking out the code, installing the necessary dependencies, and running the `aws_report_script.py` script. This automation helps in consistently executing the script in a CI/CD environment.

### Setup

1. Ensure Jenkins is installed and running.

2. Create a new Jenkins pipeline job and configure it to use the pipeline script from SCM, pointing to this repository.

3. Add your AWS credentials in Jenkins with the credentials ID `awscredentials`.

### Pipeline Execution

The pipeline will:

1. **Checkout**: Check out the latest code from the repository.
2. **Build and Run Script**:
    - Install the required Python packages using `pip`.
    - Execute the `aws_report_script.py` script.
    - Print a message indicating that the output files are stored in the Jenkins workspace.
