PYTHON ?= python3
DIST := dist/city11.sfc
APK := dist/city11.apk
ANDROID_SDK ?= $(HOME)/android-sdk

.PHONY: all rom web apk test clean

all: rom web

rom:
	$(PYTHON) tools/build_rom.py -o $(DIST)

web:
	$(PYTHON) tools/export_web.py

apk: web
	printf 'sdk.dir=%s\n' "$(ANDROID_SDK)" > android/local.properties
	cd android && ANDROID_HOME=$(ANDROID_SDK) ANDROID_SDK_ROOT=$(ANDROID_SDK) ./gradlew assembleRelease
	mkdir -p dist
	cp android/app/build/outputs/apk/release/app-release.apk $(APK)
	@echo "wrote $(APK)"

test:
	$(PYTHON) -m pytest -q

clean:
	rm -rf dist __pycache__ game/__pycache__ tools/__pycache__ tests/__pycache__ .pytest_cache
