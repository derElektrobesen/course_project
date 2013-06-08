TARGET = dFilter
 
KERNELVERSION = $(shell uname -r)
KERNELDIR = /lib/modules/$(KERNELVERSION)/build
PWD = $(shell pwd)

SRCDIR = src

SRCS = $(SRCDIR)/main.c $(SRCDIR)/keyboard.c
OBJS = $(SRCS:%.c=%.o) 

GEN_MAP_FILE = /usr/bin/python key_codes.py --gen --sourcedir=$(SRCDIR) --conffile="./key_map.conf" --out="key_map.h"

# В релиз-сборке необходим контроль всех сообщений
EXTRA_FLAGS_MY = -Werror -Wall

DEFINES = TARGET=\"$(TARGET)\",\
		  MAX_DELAY_USEC=500,\
#		  DEBUG,

# Дефайны, которые не совсем адекватно обрабаотываются 
# процедурой ниже.
# Подставляются как есть
EXTRA_DEFINES = 

EXTRA_CFLAGS = $(DEFINES:%,=-D%) $(EXTRA_DEFINES) $(EXTRA_FLAGS_MY)
	 
ifneq ($(KERNELRELEASE),)
    # Если это сборка ядра, то перечислить собираемые модули
    obj-m := $(TARGET).o
    # И файлы каждого модуля
    $(TARGET)-objs := $(OBJS)
	 
else
    # Если это не сборка ядра, то объявить целью по умолчанию
    # вызов системы сборки ядра
default:
	$(GEN_MAP_FILE)
	$(MAKE) -C $(KERNELDIR) M="$(PWD)" modules
endif
		 
clean:
	$(MAKE) -C $(KERNELDIR) M="$(PWD)" clean
	rm -f *~ ./$(SRCDIR)/*~

clean_all:
	$(MAKE) clean
	rm -f .*.swp ./$(SRCDIR)/.*.swp	
	rm -f ./$(SRCDIR)/key_map.h
