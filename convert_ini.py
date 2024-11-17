import configparser
import toml
from pathlib import Path

def ini_to_toml(ini_path: Path, toml_path: Path):
    config = configparser.ConfigParser()
    config.read(ini_path)
    config_dict = {section: dict(config.items(section)) for section in config.sections()}

    with open(toml_path, 'w') as toml_file:
        toml.dump(config_dict, toml_file)

    print(f"{ini_path.relative_to(Path.cwd())} -> {toml_path.relative_to(Path.cwd())}")

def convert_ini_directory(directory_path: Path):
    for f in directory_path.iterdir():
        if f.suffix == ".ini":
            toml_path = Path.cwd() / f"share/offsets/{f.stem}.toml"
            ini_to_toml(f, toml_path)

if __name__ == "__main__":
    ini_dir = Path.cwd() / "share/ini"
    convert_ini_directory(ini_dir)
