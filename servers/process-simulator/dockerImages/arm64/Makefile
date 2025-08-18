# Copyright (C) 2025 CEA - All Rights Reserved
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

PLATFORM=arm64
DOCKERFILE_PATH=.
DOCKER_BUILD_CONTEXT=../../..
DOCKER=DOCKER_CLI_EXPERIMENTAL=enabled docker
DOCKER_BUILD=$(DOCKER) buildx build --platform linux/$(PLATFORM) --load
DOCKER_SAVE=$(DOCKER) save
DOCKER_RMI=$(DOCKER) rmi
DOCKER_IMAGE_PREFIX=seciiot/


all: modbus argos hydro hydro-argos gas-detection

modbus:
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_PREFIX)$@:$(PLATFORM) -f $(DOCKERFILE_PATH)/Dockerfile.$@ $(DOCKER_BUILD_CONTEXT)

gpio:
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_PREFIX)$@:$(PLATFORM) -f $(DOCKERFILE_PATH)/Dockerfile.$@ $(DOCKER_BUILD_CONTEXT)

simulator:
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_PREFIX)$@:$(PLATFORM) -f $(DOCKERFILE_PATH)/Dockerfile.$@ $(DOCKER_BUILD_CONTEXT)

hydro: simulator
	$(DOCKER_BUILD) -t $(DOCKER_IMAGE_PREFIX)$@:$(PLATFORM) -f $(DOCKERFILE_PATH)/Dockerfile.simulator-$@ $(DOCKER_BUILD_CONTEXT)

.PHONY: export clean mrproper

export: modbus_arm64.tar.xz gpio_arm64.tar.xz hydro_arm64.tar.xz

%.tar.xz: 
	$(DOCKER_SAVE) $(subst .tar.xz,,$(subst _,:,$(DOCKER_IMAGE_PREFIX)$@)) | xz -z9eT16 > $@

clean:
	rm -rf *.tar.xz

mrproper: clean
	$(DOCKER_RMI) $(DOCKER_IMAGE_PREFIX)modbus:$(PLATFORM)
	$(DOCKER_RMI) $(DOCKER_IMAGE_PREFIX)gpio:$(PLATFORM)
	$(DOCKER_RMI) $(DOCKER_IMAGE_PREFIX)simulator:$(PLATFORM)
	$(DOCKER_RMI) $(DOCKER_IMAGE_PREFIX)hydro:$(PLATFORM)
