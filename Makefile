# Makefile will looks for these suffix and compile it into a usable format
# when it detects any changes. Unless you have a good reason to, do not
# touch these lines.

.SUFFIXES: .css .styl

# Configurations

STATIC=fanboi2/static
ASSETS=fanboi2/assets
VENDOR=fanboi2/vendor

# Make script

STYLUS_ARGS=-I $(VENDOR)/stylesheets -u nib -c --include-css

$(STATIC)/stylesheets/%.css: $(ASSETS)/stylesheets/%.styl
	@mkdir -p $(shell dirname $@)
	@stylus $(STYLUS_ARGS) -o $(shell dirname $@) $<
	@touch $(ASSETS)/stylesheets/main.styl

$(STATIC)/%: $(ASSETS)/%
	@mkdir -p $(shell dirname $@)
	@cp $< $@

$(STATIC)/%: $(VENDOR)/%
	@mkdir -p $(shell dirname $@)
	@cp $< $@

# Compile targets
STYL_FILES=$(shell find $(ASSETS) -type f -iname *.styl)
STYL_TARGET=$(STYL_FILES:$(ASSETS)/%.styl=$(STATIC)/%.css)

# Copy-only targets
FIND_FILTER=-type f ! -iname \*.styl ! -iname .\*
ASSETS_FILES=$(shell find $(ASSETS) $(FIND_FILTER))
ASSETS_TARGET=$(ASSETS_FILES:$(ASSETS)/%=$(STATIC)/%)
VENDOR_FILES=$(shell find $(VENDOR) $(FIND_FILTER))
VENDOR_TARGET=$(VENDOR_FILES:$(VENDOR)/%=$(STATIC)/%)

# Compile targets for our assets. By default compile all files in the assets
# directory into static directory. First target in a Makefile is a default
# target. If you type "make" then "make all" is assumed.

all: styl assets
styl: $(STYL_TARGET)
assets: $(ASSETS_TARGET) $(VENDOR_TARGET)

# Assets compilation for production deploy.

deploy: clean all
	@mv $(STATIC) $(STATIC)-compiled
	@r.js -o app.build.js
	@rm -rf $(STATIC)-compiled

# Prepare and clean for setup and teardowns.

clean:
	@rm -rf $(STATIC)

# Watcher. Use the `watch` binary to automatically compile assets on change.
# Already compiled assets will be left untouched.

watch:
	watch --interval=1 $(MAKE)
