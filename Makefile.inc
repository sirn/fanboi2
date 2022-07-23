.PHONY: help
.MAIN: help

help:
	@: # Print this help
	@printf 'Usage: make TARGET\n\n'
	@printf 'You must run make with one of the following targets to continue:\n'
	@printf 'Run make VERBOSE=1 TARGET for verbose log.\n'
	@awk ' \
		/^[^\t:]+:/ { \
			split($$0, s, ":"); \
			cmd=s[1]; \
		} /^\t@: #/ { \
			split($$0, t, ": # "); \
			body=t[2]; \
			doprnt=1; \
		} { \
			if (doprnt == 1) { \
				if (cmd != "") { \
					printf("\n\033[33m%s\033[0m:\n", cmd); \
					cmd="" \
				}; \
				printf("\t%s\n", body); \
				doprnt=0; \
				body=""; \
			}; \
		} \
	' $(.MAKE.MAKEFILES)

$(VERBOSE).SILENT:
