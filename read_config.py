import yaml


def read_config(file_path):
    with open(file_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        return config
