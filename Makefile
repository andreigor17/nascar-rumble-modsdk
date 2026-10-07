PYTHON := python3
VENV_PYTHON := .venv/bin/python
DOCKER ?= docker
DOCKER_PLATFORM ?= linux/amd64
DOCKER_IMAGE ?= rumble-decomp-ci
AS := mipsel-linux-gnu-as
LD := mipsel-linux-gnu-ld
OBJCOPY := mipsel-linux-gnu-objcopy
ASFLAGS := -no-pad-sections -march=r3000 -mabi=32 -I include

.PHONY: setup setup-ci setup-ci-deps setup-tools extract build check test test-public diff objdiff context progress \
	progress-write progress-check backlog lint-config format-check ci-public ci-full \
	docker-public docker-matching clean-generated

setup-ci-deps:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install --require-hashes -r requirements-splat.lock
	@command -v $(AS) >/dev/null || { echo "missing $(AS); on macOS run: brew install mipsel-linux-gnu-binutils"; exit 1; }
	@$(VENV_PYTHON) -m splat --version | grep -F "splat 0.50.0"
	@$(AS) --version | head -1 | grep -F "2.47"

setup-ci: setup-ci-deps
	$(PYTHON) scripts/setup_decomp_tools.py

setup: setup-ci
	$(VENV_PYTHON) -m pip install --require-hashes -r requirements-decomp.lock

extract:
	$(PYTHON) scripts/verify_reference.py
	$(PYTHON) scripts/generate_splat_symbols.py
	$(PYTHON) scripts/classify_gp_usage.py
	$(VENV_PYTHON) -m splat split config/splat.yaml

build:
	mkdir -p build/asm/data build/assets build/src/game
	$(AS) $(ASFLAGS) -o build/asm/header.o asm/header.s
	$(AS) $(ASFLAGS) -o build/asm/main_0.o asm/main_0.s
	$(PYTHON) scripts/compile_psyq.py src/game/FUN_80078c24.c build/src/game/FUN_80078c24.o
	$(AS) $(ASFLAGS) -o build/asm/main_1.o asm/main_1.s
	$(AS) $(ASFLAGS) -o build/asm/data/main.rodata.o asm/data/main.rodata.s
	$(AS) $(ASFLAGS) -o build/asm/data/main.sdata.o asm/data/main.sdata.s
	$(AS) $(ASFLAGS) -o build/asm/data/main.data.o asm/data/main.data.s
	$(AS) $(ASFLAGS) -o build/asm/data/main.bss.o asm/data/main.bss.s
	$(LD) -r -b binary -o build/assets/payload_prefix.o assets/payload_prefix.bin
	$(LD) -r -b binary -o build/assets/payload_padding.o assets/payload_padding.bin
	$(LD) -T config/undefined_funcs_auto.txt -T config/undefined_syms_auto.txt \
		-T linker/SLUS_010.68.ld -Map build/SLUS_010.68.map -o build/SLUS_010.68.elf
	$(OBJCOPY) -O binary build/SLUS_010.68.elf build/SLUS_010.68

check:
	$(PYTHON) scripts/generate_splat_symbols.py --check
	$(PYTHON) scripts/classify_gp_usage.py --check
	$(PYTHON) scripts/verify_stage2.py
	$(PYTHON) scripts/verify_stage3.py
	$(PYTHON) scripts/verify_stage4.py

test:
	$(PYTHON) -m unittest discover -s tests -v

test-public:
	RUMBLE_PUBLIC_CI=1 $(PYTHON) -m unittest discover -s tests -v

setup-tools:
	$(VENV_PYTHON) -m pip install --require-hashes -r requirements-decomp.lock
	$(PYTHON) scripts/setup_decomp_tools.py

diff:
	@test -n "$(FUNC)" || { echo "usage: make diff FUNC=FUN_80078c24"; exit 2; }
	$(VENV_PYTHON) tools/asm-differ/diff.py --no-pager --format=plain -s $(FUNC)

objdiff:
	@test -n "$(FUNC)" || { echo "usage: make objdiff FUNC=FUN_80078c24"; exit 2; }
	$(PYTHON) scripts/function_tool.py objdiff $(FUNC)

context:
	@test -n "$(FUNC)" || { echo "usage: make context FUNC=FUN_80078c24"; exit 2; }
	$(PYTHON) scripts/function_tool.py context $(FUNC)

progress:
	$(PYTHON) scripts/progress.py summary
	$(PYTHON) scripts/function_tool.py progress | sed -n '/Next leaf candidates/,$$p'

progress-write:
	$(PYTHON) scripts/progress.py write

progress-check:
	$(PYTHON) scripts/progress.py check

backlog:
	$(PYTHON) scripts/function_tool.py backlog

lint-config:
	$(PYTHON) scripts/lint_config.py

format-check:
	$(PYTHON) scripts/check_format.py

ci-public: lint-config format-check progress-check test-public

ci-full: extract build check test progress-check

docker-public:
	$(DOCKER) build --target public-ci --tag $(DOCKER_IMAGE):public .
	$(DOCKER) run --rm $(DOCKER_IMAGE):public

docker-matching:
	@test "$$($(DOCKER) version --format '{{.Server.Arch}}')" = "amd64" || { \
		echo "docker-matching requires an amd64 Docker daemon; see CONTRIBUTING.md"; exit 1; \
	}
	$(DOCKER) buildx build --platform $(DOCKER_PLATFORM) --target matching-ci \
		--tag $(DOCKER_IMAGE):matching --load .
	$(DOCKER) run --rm --platform $(DOCKER_PLATFORM) \
		--mount type=bind,source="$(CURDIR)/extracted",target=/workspace/extracted,readonly \
		--mount type=bind,source="$(CURDIR)/NASCAR Rumble (USA)",target="/workspace/NASCAR Rumble (USA)",readonly \
		$(DOCKER_IMAGE):matching make ci-full

clean-generated:
	@echo "Remove build/, asm/, assets/ and generated linker outputs manually if a fresh split is required."
