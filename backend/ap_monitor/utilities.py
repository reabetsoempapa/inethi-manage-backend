import yaml
import os
import requests
from requests.auth import HTTPBasicAuth


def reload_prometheus():
    username = 'inethi'
    password = 'iNethi2023#'

    url = 'http://inethi-prometheus:9090/-/reload'

    response = requests.post(url, auth=HTTPBasicAuth(username, password))

    print('Status Code:', response.status_code)
    print('Response:', response.text)


def update_prometheus_targets(ip_addresses):
    current_directory = os.getcwd()
    filename = 'prometheus.yml'
    full_path = os.path.join(current_directory, filename)
    print("Full path to the file:", full_path)
    with open(full_path, 'r') as file:
        data = yaml.safe_load(file)

    # Find the 'blackbox' job, append new IPs to its targets while avoiding duplicates
    for job in data.get('scrape_configs', []):
        if job['job_name'] == 'blackbox':
            current_targets = set(job['static_configs'][0]['targets'])
            updated_targets = current_targets.union(ip_addresses)
            job['static_configs'][0]['targets'] = list(updated_targets)
            break

    with open(full_path, 'w') as file:
        yaml.dump(data, file, sort_keys=False)
    # reload_prometheus()


def remove_prometheus_targets(ip_addresses):
    current_directory = os.getcwd()
    filename = 'prometheus.yml'
    full_path = os.path.join(current_directory, filename)

    with open(full_path, 'r') as file:
        data = yaml.safe_load(file)
    print('loaded yaml')
    # Find the 'blackbox' job and remove specified IPs from its targets
    for job in data.get('scrape_configs', []):
        if job['job_name'] == 'blackbox':
            current_targets = set(job['static_configs'][0]['targets'])
            updated_targets = current_targets.difference(ip_addresses)
            job['static_configs'][0]['targets'] = list(updated_targets)
            print('updated device list')
            break

    with open(full_path, 'w') as file:
        yaml.dump(data, file, sort_keys=False)
    print('written yaml')
    # reload_prometheus()


def validate_yaml(filename):
    try:
        with open(filename, 'r') as file:
            yaml.safe_load(file)
        return True
    except yaml.YAMLError as exc:
        print(f"Error in configuration file: {exc}")
        return False


if __name__ == '__main__':
    update_prometheus_targets([])
    remove_prometheus_targets(['9'])
    is_valid = validate_yaml('prometheus_test.yml')
    if is_valid:
        print("YAML file is valid")
    else:
        print("YAML file is invalid")
