# Process Simulator Usage

Process simulator relies on various docker containers linked with docker-compose.

## Docker Image Building

All docker images are located into the *dockerImages* folder.
All images are provided in both *arm64* and *amd64* architecture, exected for gpio support image only available for arm64.
Inside an architecture folder, run `make` with docker buildx installed.
If images have been crossed compiled and need to be exported, run `make export` to produce .tar.xz files for all images.
__Reminder__: For crosscompiling with docker, first follow instructions from: https://hub.docker.com/r/tonistiigi/binfmt

Example :

```sh
% cd dockerImages/amd64
% make
% make export
```

## Scenario Conception

Scenarios represent each system being simulated (ex: `hydro` is a hydroelectrical powerplant).
They are intented to be in the `scenarios` folder.
Each scenario is expected to:

- Contain a python file called with the name of the scenario (ex: `hydro.py`);
- Contain a `config.toml` file with environment and variable information (see bellow);
- A `docker-compose.yaml` file detailing how the scenario is run through docker containers.
- Communicate with other parts of the simulator through a docker network called `simulatorNetwork`.

### config.toml File

All `config.toml` files are written in TOML language and must reference two dictionnaries `environment` and `variables`.
The `[environment]` dictionnary must contain a `factor` key which value is a float and will reference the amount of time elapsed between two simulation steps.
The `[variables]` dictionnary will contain as many variables as intended by the scenario, each being a dictionnary.
Each variable will contain keys describing its behavior, such as:

- `ioType`: Can be `DIGITAL_INPUT`, `DIGITAL_OUTPUT`,`ANALOG_INPUT`, `ANALOG_OUTPUT`
- `value`: Default value when simulation starts.
- `hide`: If `true`, variable is not shown in simulator's monitoring output.
- `ioBoard`: Interface card identifier.
- `ioPort`: Port number on interface board.
- `gpioSlave`: GPIO slave identifier.
- `gpioPort`: GPIO port number.
- `modbusSlave`: Modbus slave identifier.
- `modbusAddress` Modbus address.

Example:

```toml
[environment]                                                                                            
    factor = 0.5                                    

[variables]                                         
    [variables.HYDRO_CMDO_VA_BARRAGE]
        ioBoard = 3                                 
        ioType = "DIGITAL_INPUT"   
        ioPort = 0x0A                               
        value = false
```

### Scenario Behavior

Scenarios are built uppon the `simpy` Python module.
Check IRT L6.1 document.

## Running a scenario

Scenarios cas be run using docker, either as themself or using a common launcher.

### Without Launcher

Without launcher, each scenario must contain a `docker-compose.yaml` file containing all service needed by the scenerio:

- Redis database;
- Simulator;
- Protocol handlers (MODBUS, GPIO, etc).

Then start the simulator _from the scenario's folder_ with the command:

```sh
% docker compose up -d
```

Remove the `-d` to attach the outputs of the containers.

### With Launcher

The launcher will start containers common to all scenarios (Redis broker and protocols) and
then will start scenarios depending on the value of some variable.
Start the launcher _from the process simulator's root directory_ using the command:

```sh
% docker compose up -d
```

Then start the simulator using the `launcherClient.py` script using the command:

```sh
% python launcherClient.py -s hydro  # Run the hydro scenario
% python launcherClient.py -k        # Stops current scenario
```

### Partially running a scenario (for debugging)

Containers can be started one by one with the command:

```sh
% docker compose up -d SERVICE
```

Where SERVICE is the string present in the `docker-compose.yaml` file (ex: `simulator:` or `modbus:`)

```yaml
version: "3.1"

services:
    simulator:
        image: seciiot/hydro:amd64
        container_name: simulator
        tty: true
        networks:
            - simulatorNetwork

    modbus:
        image: seciiot/modbus:amd64
        container_name: modbus
        networks:
            - simulatorNetwork
        command: "--toml /opt/process-simulator/scenarios/hydro/config.toml --slaves 1"

networks:
    simulatorNetwork:
        external: true
```

Containers entrypoints can also be swapped for shell:

```sh
% docker compose run --rm --service-ports --entrypoint [b]ash SERVICE
```

Where `--rm` will remove the temporary container after on halt (careful with
modifications made inside the container) and `--service-ports` will bind
exposed ports.
