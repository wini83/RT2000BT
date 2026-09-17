SERVICE ?= comet@$(USER).service
PYTHON := .venv/bin/python

.PHONY: help sync syntax test check status restart logs update bt-status

help:
	@echo "RT2000BT helper commands:"
	@echo "  make sync       - sync Python dependencies with uv"
	@echo "  make syntax     - compile Python files to catch syntax errors"
	@echo "  make test       - run unit tests"
	@echo "  make check      - run syntax checks and unit tests"
	@echo "  make status     - show systemd service status"
	@echo "  make restart    - restart the systemd service"
	@echo "  make logs       - follow service logs"
	@echo "  make update     - git pull, sync, check and restart"
	@echo "  make bt-status  - show Bluetooth rfkill state"
	@echo ""
	@echo "Service: $(SERVICE)"

sync:
	uv sync

syntax:
	$(PYTHON) -m py_compile comet.py config.py worker.py rt2000BT/*.py tests/*.py

test:
	$(PYTHON) -m pytest -q

check: syntax test

status:
	sudo systemctl status $(SERVICE) --no-pager

restart:
	sudo systemctl restart $(SERVICE)

logs:
	sudo journalctl -u $(SERVICE) -f

update:
	git pull
	uv sync
	$(MAKE) check
	sudo systemctl restart $(SERVICE)
	@echo "Updated, tested and restarted $(SERVICE)"

bt-status:
	rfkill list bluetooth
