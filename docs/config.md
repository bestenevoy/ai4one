# Configuration System Guide

The configuration system in `ai4one` is built around a powerful `BaseConfig` class, designed to be both easy to use and highly flexible.

## Core Concepts

By inheriting from `ai4one.config.BaseConfig`, your configuration classes automatically gain:

- Dataclass Behavior: No need for the `@dataclass` decorator.

- Multi-Format Support: Seamlessly save to and load from JSON, YAML, and TOML files.

- Command-Line Parsing: Automatically generate command-line arguments from your dataclass fields.

- Nested Configurations: Easily build complex, hierarchical configurations.

## Installation of Optional Features

While the core library is lightweight, support for YAML and TOML configuration files requires optional dependencies.

### TOML Support

To enable loading and saving of `.toml` files, install the toml extra:

```
pip install ai4one[toml]
```

### YAML Support

To enable loading and saving of `.yaml` or `.yml` files, install the yaml extra:

```
pip install ai4one[yaml]
```

Install All Features
For convenience, you can install all optional features at once:

```
pip install ai4one[all]
```

## Basic Usage

### Defining a Configuration
Simply inherit from `BaseConfig` and define your fields with type hints.

```
from ai4one.config import BaseConfig
from typing import List

class TrainConfig(BaseConfig):
    learning_rate: float = 0.001
    epochs: int = 10
    optimizer: str = "Adam"
    layers: List[int] = [512, 256]
```

### Saving and Loading from Files
The `to_file()` and `from_file()` methods automatically detect the file format based on the extension.

```
# Create an instance
config = TrainConfig(optimizer="SGD")

# Save to different formats
config.to_file("configs/training.json")
config.to_file("configs/training.yaml")
config.to_file("configs/training.toml")

# Load from a file
loaded_config = TrainConfig.from_file("configs/training.yaml")
print(loaded_config.optimizer)  # Output: SGD
```

## Command-Line Parsing
Use the `argument_parser()` class method to parse command-line arguments.

```
# In your script (e.g., train.py)
if __name__ == "__main__":
    config = TrainConfig.argument_parser()
    print(f"Using optimizer: {config.optimizer}")
```

You can then run your script from the terminal and override values:

```
python train.py --optimizer Adagrad --learning_rate 0.05
```

For a complete, runnable example demonstrating nested configurations and advanced field types, please see the `examples/example_config.py` file in the repository.