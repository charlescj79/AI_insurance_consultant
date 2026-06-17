#!/usr/bin/env python3
"""insurance-sales-mcp — 保险咨询销售 MCP Server Package

A production-ready MCP server providing insurance product query, compliance
checking, needs assessment, objection handling, and private SOP execution
tools for Hong Kong insurance advisory workflows.

Compliant with: HKIA GL-44, RL-010 cross-border sales restrictions
"""

from setuptools import setup, find_packages

setup(
    name="insurance-sales-mcp",
    version="0.1.0",
    description="Insurance Sales Advisory MCP Server — HKIA GL-44 Compliant",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Insurance Tech Commercialization Team",
    license="Apache-2.0",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "httpx>=0.27",
        "sse-starlette>=2.0",
        "pydantic>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0",
            "httpx>=0.27",
            "coverage",
        ],
        "cli": [
            "click>=8.0",
            "rich>=13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "insurance-mcp=insurance_sales_mcp.server_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
