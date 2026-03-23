# Project Rosetta Documentation

Welcome to the Project Rosetta documentation.

Project Rosetta is an open-source initiative focused on improving scenario correlation between simulation and test-track execution in ADAS verification and validation workflows. The project provides tooling to make simulation and proving-ground scenarios comparable, measurable, and reproducible.

## Purpose

In modern ADAS programs, simulation and physical test-track execution both play critical roles in development, rating, and certification. A recurring challenge is establishing reliable correlation between these two environments.

Project Rosetta addresses this challenge by defining open, interoperable workflows for scenario transformation and correlation analysis.

## Scope

Project Rosetta is centered around three core capabilities:

1. **Scenario to Test Track**  
    Generate robot-executable test-track artifacts from ASAM OpenSCENARIO and OpenDRIVE inputs.

2. **Test Track Ground Truth to Scenario**  
    Reconstruct OpenSCENARIO and/or OpenDRIVE representations from measured test-track ground-truth data.

3. **Scenario Correlation**  
    Define and compute metrics that quantify correlation between simulated trajectories and test-track trajectories at scenario level.

## Business and Engineering Rationale

Project Rosetta is designed to support:

- Better traceability between simulation evidence and track evidence
- More efficient validation workflows for rating and certification use cases
- Shared implementation effort across partners facing the same technical problem
- Open standards adoption and interoperability in the toolchain

## Project Principles

- **Open standards first**: use and extend industry standards such as ASAM OpenSCENARIO and OpenDRIVE.
- **Reproducibility**: produce deterministic and reviewable scenario transformations.
- **Collaboration**: enable contributions from OEMs, tool vendors, research organizations, and the open-source community.
- **Measurability**: provide explicit metrics for scenario-level correlation, not only qualitative assessment.

## Documentation Map

- [Getting Started](getting-started/README.md): onboarding, setup, and first contribution flow.
- [FAQ](faq/faq.md): frequently asked questions about project use and contribution.

Additional technical content (architecture, data model, interfaces, and metric definitions) will be expanded in this documentation space as the project evolves.

## Intended Audience

This documentation is intended for:

- ADAS simulation and V&V engineers
- Test-track automation and robotics engineers
- Toolchain and data pipeline developers
- Researchers and partners contributing scenario conversion and correlation methods

## License

Project Rosetta is licensed under **MPL 2.0**.

## Contributing

To contribute, please follow the repository contribution policy in [CONTRIBUTING.md](../CONTRIBUTING.md).
