""" Command line interface """
import json

import click

from . import custom_json_loads, generate_json


@click.command()
@click.argument("schema-file", type=click.File("r"))
@click.option("-c", "--count",
              default=1,
              help="Number of samples to generate")
@click.option("-o", "--output-filename-prefix",
              help="If given, write samples to files with the format \
                    {prefix}{num}.json")
def generate_json_command(schema_file, count, output_filename_prefix):
    """ Generate JSON from schema using the command line """
    schema = custom_json_loads(schema_file.read())
    for index in range(count):
        output_json = generate_json(schema)
        if output_filename_prefix:
            with open(f"{output_filename_prefix}{index}.json", "w+") as file:
                json.dump(output_json, file, default=str)
        else:
            print(output_json)


generate_json_command.main(prog_name="json_schema_fuzz")
