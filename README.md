# JSON Schema Fuzz

This project aims to create randomized JSON files that conform to a 
user-defined JSON Schema. Although this 'fuzzer' is still in an early stage, 
the goal is to develop a tool for creating random data to be used for testing 
applications that recieve a high volume of JSON data.

Currently this tool is tied to *JSON Schema Draft 7*. 
Support for more recent JSON Schema versions are planned
for the future.

## Usage

This tool can be imported as a module or run from the command line. To see usage information about the command line tool use the following command:

```bash
python -m json_schema_fuzz --help
```

---

This application is under development at **CoVar Applied Technologies Inc.**
