# Process Simulator Architecture

Process simulator aims to a modular architecture revolving on two common modules:

- A configuration file per scenario named ```config.toml```
- A Redis database

All modules (including the simulator itself) will read their config from the
```config.toml``` file and then read/write from the Redis database.
Specific care will need to be taken when designing variables since no
protection is offered against (e.g., make sure that a variable is an output of
Modbus and an input of the simulator but not an output of both Modbus and the
simulator).

Image bellow summarizes the architecture (gree modules are implemented).

```mermaid
flowchart TD
    style Redis fill:#0f0,stroke:#333,stroke-width:4px
    style TOML fill:#0f0,stroke:#333,stroke-width:4px
    style Simulator fill:#0f0,stroke:#333,stroke-width:4px
    style Modbus fill:#0f0,stroke:#333,stroke-width:4px
    style GPIO fill:#0f0,stroke:#333,stroke-width:4px

    Other[...]

    Redis <-->|Reads/Writes Data| Simulator & Modbus & InterfaceBoard & Rest & GPIO & Other
    Rest & Modbus & Simulator & InterfaceBoard & GPIO & Other <-->|Reads Config| TOML
    Rest <--> MongoDB
```
