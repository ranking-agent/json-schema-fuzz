"""Merging."""


def merge(schema_a, schema_b):
    """Merge two JSON schemas."""
    return {
        **schema_a,
        **schema_b,
    }
