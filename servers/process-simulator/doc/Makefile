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

src_files := $(wildcard *.md) 
out_files := $(patsubst %.md,output/%.png,$(src_files))

.PHONY: all clean

all: clean $(out_files)

output/%.png: %.md
	mkdir -p $(dir $@)
	mmdc -c ./mermaid.json \
		-i $< \
		-o $@

clean:
	rm -rf output
