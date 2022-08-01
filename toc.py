from behave.configuration import Configuration
from behave.runner import Runner
from behave.runner_util import parse_features
from jinja2 import Environment, PackageLoader


def render(features):
    env = Environment(loader=PackageLoader("docs"))

    template = env.get_template("toc.template")
    template.stream(features=features).dump("docs/toc.md")


def main():
    configuration = Configuration()
    runner = Runner(config=configuration)
    runner.setup_paths()
    feature_locations = runner.feature_locations()
    features = parse_features(feature_locations)
    render(features)


if __name__ == "__main__":
    main()
