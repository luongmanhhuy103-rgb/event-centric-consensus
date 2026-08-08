CONTIKI_PROJECT = consensus-node
all: $(CONTIKI_PROJECT)

MODULES += os/net/app-layer/simple-udp

CFLAGS += -DPROJECT_CONF_H=\"project-conf.h\"
LDFLAGS += -lm

include ../../Makefile.include
